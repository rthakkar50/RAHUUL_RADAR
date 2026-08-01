import unittest
from enterprise.user_manager import EnterpriseUserManager
from enterprise.role_manager import RolePermissionManager
from enterprise.permission_engine import PermissionEngine
from enterprise.session_manager import EnterpriseSessionManager
from enterprise.organization_manager import OrganizationManager
from enterprise.api_key_manager import APIKeyManager
from enterprise.license_manager import LicenseManager
from enterprise.audit_permissions import GovernanceAuditCenter
from enterprise.enterprise_reports import EnterpriseReportEngine


class TestEnterpriseGovernance(unittest.TestCase):

    def setUp(self):
        self.user_manager = EnterpriseUserManager()
        self.role_manager = RolePermissionManager()
        self.permission_engine = PermissionEngine()
        self.session_manager = EnterpriseSessionManager()
        self.org_manager = OrganizationManager()
        self.api_key_manager = APIKeyManager()
        self.license_manager = LicenseManager()
        self.audit_center = GovernanceAuditCenter()
        self.report_engine = EnterpriseReportEngine()

    def test_task_1_user_roles(self):
        """Task 1: User Management supporting Admin, Trader, Viewer, Researcher, Operator, Guest."""
        u1 = self.user_manager.create_user("admin_user", "admin@radar.internal", role="ADMIN")
        u2 = self.user_manager.create_user("trader_user", "trader@radar.internal", role="TRADER")
        u3 = self.user_manager.create_user("viewer_user", "viewer@radar.internal", role="VIEWER")
        u4 = self.user_manager.create_user("research_user", "research@radar.internal", role="RESEARCHER")
        u5 = self.user_manager.create_user("ops_user", "ops@radar.internal", role="OPERATOR")
        u6 = self.user_manager.create_user("guest_user", "guest@radar.internal", role="GUEST")

        self.assertEqual(len(self.user_manager.list_users()), 6)
        self.assertEqual(u1.role, "ADMIN")

    def test_task_2_rbac_permission_matrix(self):
        """Task 2: Role Based Access Control (RBAC)."""
        self.assertTrue(self.permission_engine.authorize_request("ADMIN", "trade:execute"))
        self.assertTrue(self.permission_engine.authorize_request("TRADER", "trade:execute"))
        self.assertFalse(self.permission_engine.authorize_request("VIEWER", "trade:execute"))
        self.assertTrue(self.permission_engine.authorize_request("RESEARCHER", "quant:analyze"))

    def test_task_3_and_8_sessions_and_rate_limiting(self):
        """Task 3 & Task 8: Authentication, Sessions, Brute Force, and Rate Limiting."""
        sess = self.session_manager.create_session("USR-1234")
        self.assertTrue(self.session_manager.validate_session(sess.token))

        # Brute Force
        for _ in range(5):
            self.session_manager.record_login_attempt("attacker", success=False)
        self.assertTrue(self.session_manager.check_brute_force_lock("attacker"))

        # Rate limiting
        self.assertTrue(self.session_manager.check_rate_limit("client_1", limit_seconds=1.0))
        self.assertFalse(self.session_manager.check_rate_limit("client_1", limit_seconds=1.0))

    def test_task_4_multi_tenant_organizations(self):
        """Task 4: Multi-Tenant Organizations."""
        org = self.org_manager.create_organization("HedgeFund Alpha", license_tier="INSTITUTIONAL", max_users=100)
        self.assertEqual(org.license_tier, "INSTITUTIONAL")
        self.assertIsNotNone(self.org_manager.get_organization(org.org_id))

    def test_task_5_api_key_management(self):
        """Task 5: API Key Generation, Rotation, and Revocation."""
        key = self.api_key_manager.create_api_key("USR-123", "ORG-456", "Production_Key")
        self.assertTrue(key.is_active)

        rotated = self.api_key_manager.rotate_api_key(key.key_id)
        self.assertFalse(key.is_active)
        self.assertTrue(rotated.is_active)

        self.api_key_manager.revoke_api_key(rotated.key_id)
        self.assertFalse(rotated.is_active)

    def test_task_6_license_tiers(self):
        """Task 6: License Tiers (Free, Pro, Enterprise, Institutional)."""
        self.assertTrue(self.license_manager.is_module_allowed("FREE", "dashboard"))
        self.assertFalse(self.license_manager.is_module_allowed("FREE", "fno_engine"))
        self.assertTrue(self.license_manager.is_module_allowed("ENTERPRISE", "fno_engine"))

    def test_task_7_governance_audit_logging(self):
        """Task 7: Governance Audit Logging."""
        entry = self.audit_center.record_governance_event("USR-ADMIN", "ORG-DEFAULT", "AI_PROMOTION", {"challenger": "AI_v3"})
        self.assertEqual(entry.action_type, "AI_PROMOTION")
        self.assertEqual(len(self.audit_center.get_audit_records()), 1)

    def test_task_9_and_10_reports_and_backward_compatibility(self):
        """Task 9 & Task 10: Governance Reports & Single-User Backward Compatibility."""
        rep = self.report_engine.generate_full_report()
        self.assertEqual(rep["compliance_readiness"], "SOC-2 Type II & ISO-27001 Audit Ready")

        # Task 10: Single-User Default Mode works seamlessly without explicit org setup
        default_org = self.org_manager.get_organization("ORG-DEFAULT")
        self.assertIsNotNone(default_org)


if __name__ == "__main__":
    unittest.main()
