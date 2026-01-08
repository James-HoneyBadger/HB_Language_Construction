import pytest
from src.parsercraft.enterprise_security import (
    RBACManager, SSOAuthenticationManager, VulnerabilityScanner,
    Role, Permission, SSOProvider, User, VulnerabilityLevel
)

def test_rbac_user_creation_and_permissions():
    rbac = RBACManager()
    user = rbac.create_user("alice", "alice@example.com", roles={Role.VIEWER})
    
    # Viewer should have READ_CONFIG but not WRITE_CONFIG
    assert rbac.check_permission(user.user_id, Permission.READ_CONFIG)
    assert not rbac.check_permission(user.user_id, Permission.WRITE_CONFIG)
    
    # Upgrade to Developer
    rbac.assign_role(user.user_id, Role.DEVELOPER)
    assert rbac.check_permission(user.user_id, Permission.WRITE_CONFIG)
    assert rbac.check_permission(user.user_id, Permission.EXECUTE_CODE)
    
    # Audit log check
    log = rbac.get_audit_log()
    assert len(log) >= 2
    assert log[-2]["action"] == "user_created"
    assert log[-1]["action"] == "role_assigned"

def test_sso_flow():
    sso = SSOAuthenticationManager()
    sso.register_provider(
        SSOProvider.GITHUB,
        "id", "secret", "github.com", "callback"
    )
    
    # Authenticate
    result = sso.authenticate(SSOProvider.GITHUB, "auth_code")
    assert result["status"] == "success"
    session_id = result["session_id"]
    
    # Validate
    assert sso.validate_session(session_id)
    
    # Logout
    sso.logout(session_id)
    assert not sso.validate_session(session_id)

def test_vulnerability_scanner_secrets():
    scanner = VulnerabilityScanner()
    code = 'api_key = "12345"'
    vulns = scanner.scan_code(code, "test.py")
    
    assert len(vulns) >= 1
    assert vulns[0].title == "Hardcoded Secret"
    assert vulns[0].level == VulnerabilityLevel.CRITICAL

def test_vulnerability_scanner_sql_injection():
    scanner = VulnerabilityScanner()
    code = 'cursor.execute("SELECT * FROM users WHERE name = " + user_input)'
    vulns = scanner.scan_code(code, "db.py")
    
    assert len(vulns) >= 1
    assert vulns[0].title == "Potential SQL Injection"

def test_vulnerability_scanner_xss():
    scanner = VulnerabilityScanner()
    code = 'document.getElementById("t").innerHTML = userInput;'
    vulns = scanner.scan_code(code, "ui.js")
    
    assert len(vulns) >= 1
    assert vulns[0].title == "Potential Cross-Site Scripting (XSS)"
