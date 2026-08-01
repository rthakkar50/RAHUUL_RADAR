import unittest
from ops.health_monitor import SystemHealthMonitor
from ops.metrics_collector import MetricsCollector
from ops.alert_manager import AlertManager
from ops.audit_center import AuditCenter
from ops.backup_manager import BackupManager
from ops.restore_manager import RestoreManager
from ops.config_manager import ConfigManager
from ops.system_diagnostics import SystemDiagnostics
from ops.log_center import CentralLogCenter
from ops.deployment_manager import DeploymentManager
from ops.ops_reports import OpsReportEngine


class TestOpsPlatform(unittest.TestCase):

    def setUp(self):
        self.health_monitor = SystemHealthMonitor()
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.audit_center = AuditCenter()
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager()
        self.config_manager = ConfigManager()
        self.diagnostics = SystemDiagnostics()
        self.log_center = CentralLogCenter()
        self.deployment_manager = DeploymentManager()
        self.ops_report_engine = OpsReportEngine()

    def test_task_1_health_monitor(self):
        """Task 1: System Health Monitoring."""
        health = self.health_monitor.check_system_health()
        self.assertIn(health.overall_status, ["HEALTHY", "DEGRADED", "UNHEALTHY"])
        self.assertGreaterEqual(health.memory_pct, 0.0)

    def test_task_2_metrics_collector(self):
        """Task 2: Performance Metrics Collection."""
        metrics = self.metrics_collector.collect_all_metrics()
        self.assertTrue(len(metrics) >= 5)

    def test_task_3_alert_manager(self):
        """Task 3: Incident & Alert Management."""
        alert = self.alert_manager.create_custom_alert("WARNING", "AI_ENGINE", "Model Drift Alert", "PSI exceeded 0.20 threshold")
        self.assertEqual(alert.severity, "WARNING")
        self.assertEqual(len(self.alert_manager.get_active_alerts()), 1)

    def test_task_4_audit_center_sensitive_redaction(self):
        """Task 4: Audit Center & Sensitive Credential Redaction."""
        entry = self.audit_center.record_audit_event(
            event_type="ORDER_EXECUTED",
            source_module="PaytmOrderEngine",
            action="PLACE_ORDER",
            details={"symbol": "RELIANCE", "api_key": "SECRET_KEY_12345", "price": 2980.0}
        )
        self.assertTrue(entry.sensitive_redacted)
        self.assertEqual(entry.details["api_key"], "[REDACTED_CREDENTIAL]")

    def test_task_5_backup_and_restore_verification(self):
        """Task 5: SQLite & Registry Backup & Restore Verification."""
        backup = self.backup_manager.create_full_backup()
        self.assertTrue(backup.is_verified)
        self.assertTrue(len(backup.checksum) > 0)

        restore = self.restore_manager.verify_and_restore(backup)
        self.assertTrue(restore.is_successful)

    def test_task_6_7_config_and_diagnostics(self):
        """Task 6 & 7: Configuration Integrity & System Diagnostics."""
        cfg = self.config_manager.validate_configuration()
        self.assertTrue(cfg.is_valid)

        diag = self.diagnostics.generate_full_diagnostics()
        self.assertIn("system_report", diag)
        self.assertIn("performance_report", diag)

    def test_task_8_9_log_center_and_deployment_manager(self):
        """Task 8 & 9: Log Center & Render Deployment Verification."""
        self.log_center.log_event("INFO", "SRE", "Deployment test PAYTM_API_KEY")

        dep = self.deployment_manager.verify_deployment()
        self.assertTrue(dep["deployment_verified"])
        self.assertEqual(dep["health_status"], "200 OK")

    def test_cto_operations_report(self):
        """CTO Operations Report generation test."""
        rep = self.ops_report_engine.generate_cto_operations_report()
        self.assertEqual(rep["operational_readiness"], "100% PRODUCTION READY")


if __name__ == "__main__":
    unittest.main()
