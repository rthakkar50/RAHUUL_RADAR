import json
import logging
import csv
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalQualityService:
    def __init__(self, config_path: str = "config/dashboard_quality.json"):
        self.config_path = config_path
        self.config = {}
        self.load_dashboard()

    def load_dashboard(self):
        """Loads dashboard configuration."""
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            logger.info("Signal Quality Dashboard Config Loaded")
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.config = {
                "refresh_interval_ms": 5000,
                "gauge_thresholds": {"good_min": 75.0, "warning_min": 40.0, "critical_max": 39.9},
                "warning_levels": {"memory_warning_mb": 1024.0, "cpu_warning_pct": 75.0, "latency_warning_ms": 300.0},
                "panel_visibility": {},
                "export_settings": {"default_export_path": "exports/", "enable_pdf_export": True, "enable_csv_export": True}
            }

    def collect_engine_results(self, mock_data: dict = None) -> dict:
        """Aggregates data from all backend engines."""
        if mock_data is not None:
            return mock_data
            
        # In a real scenario, this would query MasterSignalPipeline or a central state store.
        # Here we return a default structure representing the fetched state.
        return {
            "confidence_score": 0.0,
            "recent_signals": [],
            "top_strategy": "None",
            "market_status": "Unknown",
            "performance": {
                "latency_ms": 0.0,
                "memory_mb": 0.0,
                "cpu_pct": 0.0
            },
            "validation": {
                "walk_forward_status": "PENDING",
                "institution_score": 0.0
            },
            "engines_health": {
                "trend": True,
                "momentum": True,
                "volume": True,
                "structure": True,
                "risk": True
            }
        }

    def calculate_overall_quality(self, data: dict) -> float:
        """Calculates a 0-100 quality score based on aggregated data."""
        # A simple aggregation logic based on confidence, performance penalties, and validation score.
        confidence = data.get("confidence_score", 0.0)
        perf = data.get("performance", {})
        
        latency = perf.get("latency_ms", 0.0)
        memory = perf.get("memory_mb", 0.0)
        cpu = perf.get("cpu_pct", 0.0)
        
        # Penalties
        warn_levels = self.config.get("warning_levels", {})
        latency_warn = warn_levels.get("latency_warning_ms", 300.0)
        mem_warn = warn_levels.get("memory_warning_mb", 1024.0)
        cpu_warn = warn_levels.get("cpu_warning_pct", 75.0)
        
        penalty = 0.0
        if latency > latency_warn: penalty += 10.0
        if memory > mem_warn: penalty += 10.0
        if cpu > cpu_warn: penalty += 10.0
        
        val_score = data.get("validation", {}).get("institution_score", 0.0)
        
        # Base quality is average of confidence and validation, minus performance penalties
        quality = ((confidence + val_score) / 2.0) - penalty
        return max(0.0, min(100.0, quality))

    def calculate_health_score(self, data: dict) -> str:
        """Returns GREEN, YELLOW, or RED based on engine statuses."""
        health = data.get("engines_health", {})
        if not health:
            return "RED"
            
        failed_count = sum(1 for status in health.values() if not status)
        total = len(health)
        
        if failed_count == 0:
            return "GREEN"
        elif failed_count <= total * 0.3: # Up to 30% failure is yellow
            return "YELLOW"
        else:
            return "RED"

    def calculate_signal_distribution(self, data: dict) -> dict:
        """Calculates statistics on recent signals."""
        signals = data.get("recent_signals", [])
        total = len(signals)
        if total == 0:
            return {"total": 0, "buy": 0, "sell": 0, "watch": 0}
            
        buy = sum(1 for s in signals if s.get("action", "").upper() == "BUY")
        sell = sum(1 for s in signals if s.get("action", "").upper() == "SELL")
        watch = sum(1 for s in signals if s.get("action", "").upper() == "WATCH")
        
        return {"total": total, "buy": buy, "sell": sell, "watch": watch}

    def generate_summary(self, data: dict) -> dict:
        quality = self.calculate_overall_quality(data)
        health = self.calculate_health_score(data)
        distribution = self.calculate_signal_distribution(data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_quality": quality,
            "health_status": health,
            "confidence_score": data.get("confidence_score", 0.0),
            "top_strategy": data.get("top_strategy", "None"),
            "market_status": data.get("market_status", "Unknown"),
            "performance": data.get("performance", {}),
            "validation": data.get("validation", {}),
            "signal_distribution": distribution,
            "recent_signals": data.get("recent_signals", [])
        }

    def refresh_dashboard(self, mock_data: dict = None) -> dict:
        """Main entrypoint to fetch fresh data for the UI without blocking."""
        try:
            data = self.collect_engine_results(mock_data)
            summary = self.generate_summary(data)
            logger.info("Dashboard Refresh Complete")
            return summary
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            return {"error": str(e), "overall_quality": 0.0, "health_status": "RED"}

    def export_dashboard(self, data: dict, format_type: str = "JSON", output_dir: str = None) -> str:
        """Exports the dashboard summary to a file."""
        if not data:
            raise ValueError("No data to export")
            
        export_settings = self.config.get("export_settings", {})
        out_dir = output_dir or export_settings.get("default_export_path", "exports/")
        os.makedirs(out_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        format_type = format_type.upper()
        if format_type == "JSON":
            filepath = os.path.join(out_dir, f"dashboard_export_{timestamp}.json")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        elif format_type == "CSV" and export_settings.get("enable_csv_export", True):
            filepath = os.path.join(out_dir, f"dashboard_export_{timestamp}.csv")
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Timestamp", data.get("timestamp")])
                writer.writerow(["Overall Quality", data.get("overall_quality")])
                writer.writerow(["Health Status", data.get("health_status")])
                writer.writerow(["Confidence Score", data.get("confidence_score")])
                writer.writerow(["Top Strategy", data.get("top_strategy")])
                writer.writerow(["Market Status", data.get("market_status")])
                perf = data.get("performance", {})
                writer.writerow(["Latency (ms)", perf.get("latency_ms")])
                writer.writerow(["Memory (MB)", perf.get("memory_mb")])
                writer.writerow(["CPU (%)", perf.get("cpu_pct")])
        elif format_type == "PDF" and export_settings.get("enable_pdf_export", True):
            filepath = os.path.join(out_dir, f"dashboard_export_{timestamp}.pdf")
            # Mock PDF generation
            with open(filepath, "w") as f:
                f.write("Mock PDF Output\n")
                f.write(json.dumps(data, indent=2))
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
            
        logger.info(f"Export Complete: {filepath}")
        return filepath
