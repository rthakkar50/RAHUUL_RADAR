import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class OptimizationStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    GOOD = "GOOD"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class OptimizationLevel(str, Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    AGGRESSIVE = "AGGRESSIVE"

@dataclass
class PerformanceMetrics:
    execution_time_ms: float
    cpu_usage: float
    memory_usage_mb: float
    cache_hit_ratio: float
    thread_count: int
    queue_size: int
    optimization_score: float

    def to_dict(self) -> dict:
        return {
            "execution_time_ms": self.execution_time_ms,
            "cpu_usage": self.cpu_usage,
            "memory_usage_mb": self.memory_usage_mb,
            "cache_hit_ratio": self.cache_hit_ratio,
            "thread_count": self.thread_count,
            "queue_size": self.queue_size,
            "optimization_score": self.optimization_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PerformanceMetrics':
        return cls(
            execution_time_ms=float(data.get("execution_time_ms", 0.0)),
            cpu_usage=float(data.get("cpu_usage", 0.0)),
            memory_usage_mb=float(data.get("memory_usage_mb", 0.0)),
            cache_hit_ratio=float(data.get("cache_hit_ratio", 0.0)),
            thread_count=int(data.get("thread_count", 0)),
            queue_size=int(data.get("queue_size", 0)),
            optimization_score=float(data.get("optimization_score", 0.0))
        )

@dataclass
class OptimizationResult:
    status: str
    optimization_level: str
    recommendations: List[str]
    warnings: List[str]
    metrics: dict

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "optimization_level": self.optimization_level,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "metrics": self.metrics
        }


class PerformanceOptimizer:
    def __init__(self, config_path: str = "config/performance_optimizer.json"):
        self.config_path = config_path
        self.thresholds = {}
        self.settings = {}
        self.load_configuration()
        self.validate_configuration()

    def load_configuration(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.thresholds = data.get("performance_thresholds", {})
                self.settings = data.get("optimization_settings", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self._load_defaults()

    def _load_defaults(self):
        self.thresholds = {
            "maximum_cpu_percent": 80.0,
            "maximum_memory_mb": 1024.0,
            "target_execution_time_ms": 500.0,
            "maximum_threads": 8,
            "cache_size_mb": 256.0
        }
        self.settings = {
            "default_optimization_level": "STANDARD",
            "aggressive_cpu_threshold": 90.0,
            "aggressive_memory_threshold": 2048.0
        }

    def validate_configuration(self):
        # Basic sanity checks on config to prevent div by zero or negative bounds
        if self.thresholds.get("maximum_cpu_percent", 0) <= 0:
            self.thresholds["maximum_cpu_percent"] = 80.0
        if self.thresholds.get("maximum_memory_mb", 0) <= 0:
            self.thresholds["maximum_memory_mb"] = 1024.0
        if self.thresholds.get("target_execution_time_ms", 0) <= 0:
            self.thresholds["target_execution_time_ms"] = 500.0

    def analyze_cpu(self, cpu_usage: float) -> (float, str):
        """Returns normalized score (0-100, 100 being worst) and analysis note."""
        max_cpu = self.thresholds.get("maximum_cpu_percent", 80.0)
        aggr_cpu = self.settings.get("aggressive_cpu_threshold", 90.0)
        
        score = (cpu_usage / max_cpu) * 100.0 if max_cpu > 0 else 100.0
        
        if cpu_usage > aggr_cpu:
            return min(100.0, score), "CRITICAL: CPU usage dangerously high."
        elif cpu_usage > max_cpu:
            return min(100.0, score), "WARNING: CPU usage exceeds target threshold."
        return max(0.0, score), "GOOD: CPU usage within limits."

    def analyze_memory(self, memory_mb: float) -> (float, str):
        max_mem = self.thresholds.get("maximum_memory_mb", 1024.0)
        aggr_mem = self.settings.get("aggressive_memory_threshold", 2048.0)
        
        score = (memory_mb / max_mem) * 100.0 if max_mem > 0 else 100.0
        
        if memory_mb > aggr_mem:
            return min(100.0, score), "CRITICAL: Memory footprint dangerously high."
        elif memory_mb > max_mem:
            return min(100.0, score), "WARNING: Memory usage exceeds target threshold."
        return max(0.0, score), "GOOD: Memory footprint within limits."

    def analyze_execution_time(self, exec_time: float) -> (float, str):
        target_exec = self.thresholds.get("target_execution_time_ms", 500.0)
        score = (exec_time / target_exec) * 100.0 if target_exec > 0 else 100.0
        
        if exec_time > target_exec * 2:
            return min(100.0, score), "CRITICAL: Severe latency detected."
        elif exec_time > target_exec:
            return min(100.0, score), "WARNING: Execution latency is above target."
        return max(0.0, score), "GOOD: Execution speed is optimal."

    def analyze_cache(self, hit_ratio: float) -> (float, str):
        # 100% hit ratio is 0 penalty, 0% hit ratio is 100 penalty
        penalty = 100.0 - (hit_ratio * 100.0) if hit_ratio <= 1.0 else 0.0
        
        if hit_ratio < 0.2:
            return penalty, "CRITICAL: Cache efficiency is very low."
        elif hit_ratio < 0.5:
            return penalty, "WARNING: Cache hit ratio could be improved."
        return penalty, "GOOD: Cache efficiency is healthy."

    def validate_metrics(self, metrics: PerformanceMetrics) -> bool:
        if metrics.execution_time_ms < 0:
            return False
        if metrics.cpu_usage < 0 or metrics.cpu_usage > 100:
            return False
        if metrics.memory_usage_mb < 0:
            return False
        if metrics.cache_hit_ratio < 0 or metrics.cache_hit_ratio > 1.0:
            return False
        if metrics.thread_count < 0:
            return False
        return True

    def collect_metrics(self, raw_metrics: PerformanceMetrics) -> OptimizationResult:
        start_time = __import__("datetime").datetime.now()
        logger.info("Performance Optimization Start")
        
        warnings = []
        recommendations = []
        
        if not self.validate_metrics(raw_metrics):
            return OptimizationResult(
                status=OptimizationStatus.CRITICAL.value,
                optimization_level=OptimizationLevel.AGGRESSIVE.value,
                recommendations=["Metrics validation failed. Check telemetry systems."],
                warnings=["Received invalid metrics (e.g. negative execution time)."],
                metrics=raw_metrics.to_dict()
            )

        # Higher penalty score = worse performance
        cpu_score, cpu_msg = self.analyze_cpu(raw_metrics.cpu_usage)
        mem_score, mem_msg = self.analyze_memory(raw_metrics.memory_usage_mb)
        exec_score, exec_msg = self.analyze_execution_time(raw_metrics.execution_time_ms)
        cache_score, cache_msg = self.analyze_cache(raw_metrics.cache_hit_ratio)
        
        if "CRITICAL" in cpu_msg or "WARNING" in cpu_msg:
            warnings.append(cpu_msg)
        if "CRITICAL" in mem_msg or "WARNING" in mem_msg:
            warnings.append(mem_msg)
        if "CRITICAL" in exec_msg or "WARNING" in exec_msg:
            warnings.append(exec_msg)
        if "CRITICAL" in cache_msg or "WARNING" in cache_msg:
            warnings.append(cache_msg)

        avg_penalty = (cpu_score + mem_score + exec_score + cache_score) / 4.0
        
        # Optimization score (100 = perfect, 0 = worst)
        opt_score = max(0.0, 100.0 - avg_penalty)
        raw_metrics.optimization_score = opt_score
        
        # Determine Status and Level
        if opt_score > 85.0:
            status = OptimizationStatus.OPTIMAL
            level = OptimizationLevel.NONE
        elif opt_score > 70.0:
            status = OptimizationStatus.GOOD
            level = OptimizationLevel.BASIC
            recommendations.extend(self.optimize_cache())
        elif opt_score > 40.0:
            status = OptimizationStatus.WARNING
            level = OptimizationLevel.STANDARD
            recommendations.extend(self.optimize_cache())
            recommendations.extend(self.optimize_thread_pool())
        else:
            status = OptimizationStatus.CRITICAL
            level = OptimizationLevel.AGGRESSIVE
            recommendations.extend(self.optimize_cache())
            recommendations.extend(self.optimize_thread_pool())
            recommendations.extend(self.clear_unused_cache())

        result = OptimizationResult(
            status=status.value,
            optimization_level=level.value,
            recommendations=recommendations,
            warnings=warnings,
            metrics=raw_metrics.to_dict()
        )
        
        elapsed = (__import__("datetime").datetime.now() - start_time).total_seconds()
        logger.info(f"Performance Optimization Complete in {elapsed:.3f}s")
        return result

    def optimize_cache(self) -> List[str]:
        return ["Action Required: Increase cache TTL for frequently requested structural data."]

    def optimize_thread_pool(self) -> List[str]:
        max_threads = self.thresholds.get("maximum_threads", 8)
        return [f"Action Required: Throttle thread pool to {max_threads} concurrent workers to reduce context switching."]

    def clear_unused_cache(self) -> List[str]:
        return ["Emergency Action: Flush non-essential cache partitions to reclaim memory."]

    def generate_report(self, result: OptimizationResult) -> dict:
        return {
            "Performance Status": result.status,
            "Target Optimization Level": result.optimization_level,
            "System Metrics": result.metrics,
            "Critical Warnings": result.warnings,
            "Engine Recommendations": result.recommendations
        }
