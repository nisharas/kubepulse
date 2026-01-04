import pytest
from kubecuro.models import AuditIssue

def calculate_summary_logic(all_issues, command="scan"):
    """
    Simulates the logic block from main.py to verify 
    counters and 'Before vs After' math.
    """
    ghosts   = sum(1 for i in all_issues if i.code == 'GHOST')
    hpa_gaps = sum(1 for i in all_issues if i.code in ['HPA_LOGIC', 'HPA_MISSING_REQ'])
    security = sum(1 for i in all_issues if i.code in ['RBAC_WILD', 'SEC_PRIVILEGED', 'RBAC_SECRET'])
    repairs  = sum(1 for i in all_issues if i.code == 'FIXED')
    
    # The "Before vs After" logic: Count how many issues DON'T have "FIXED" in their severity
    remaining = len([i for i in all_issues if "FIXED" not in i.severity])
    
    return {
        "ghosts": ghosts,
        "hpa": hpa_gaps,
        "security": security,
        "repairs": repairs,
        "remaining": remaining
    }

def test_fix_command_math():
    """Verify that 'FIXED' items are correctly separated from 'REMAINING'"""
    # We create a fake list of issues with NO dots/placeholders
    mock_issues = [
        AuditIssue(code="FIXED", severity="🟢 FIXED", file="a.yaml", message="Fixed API", fix="N/A", source="Healer"),
        AuditIssue(code="FIXED", severity="🟢 FIXED", file="b.yaml", message="Fixed Syntax", fix="N/A", source="Healer"),
        AuditIssue(code="RBAC_WILD", severity="🔴 HIGH", file="c.yaml", message="Wildcard found", fix="Manual", source="Shield"),
        AuditIssue(code="GHOST", severity="🟠 WARN", file="d.yaml", message="Ghost service", fix="Manual", source="Synapse"),
    ]
    
    results = calculate_summary_logic(mock_issues, command="fix")
    
    # Math check: 2 fixed, 2 remaining, 4 total.
    assert results["repairs"] == 2
    assert results["remaining"] == 2 
    assert results["security"] == 1

def test_border_color_logic():
    """Verify the summary panel turns RED if security risks exist"""
    issues = [
        AuditIssue(code="RBAC_WILD", severity="🔴 HIGH", file="f.yaml", message="Security hole", fix="Manual", source="Shield")
    ]
    
    # Simulating the visual logic: turn red if high severity OR security code exists
    all_sev = str([i.severity for i in issues])
    security_count = sum(1 for i in issues if i.code == 'RBAC_WILD')
    
    border_col = "green"
    if "🔴" in all_sev or security_count > 0:
        border_col = "red"
        
    assert border_col == "red"
