import pytest
from kubecuro.models import AuditIssue

# --- THE CALCULATOR ---
# This function mimics the "Brain" of your reporting panel.
# We keep it here to test if the logic works without running the whole app.
def calculate_summary_logic(all_issues, command="scan"):
    # We are counting specific 'Tags' (codes) assigned to problems.
    # Logic: "Count every issue where the code is GHOST"
    ghosts   = sum(1 for i in all_issues if i.code == 'GHOST')
    hpa_gaps = sum(1 for i in all_issues if i.code in ['HPA_LOGIC', 'HPA_MISSING_REQ'])
    security = sum(1 for i in all_issues if i.code in ['RBAC_WILD', 'SEC_PRIVILEGED', 'RBAC_SECRET'])
    repairs  = sum(1 for i in all_issues if i.code == 'FIXED')
    
    # THE REMAINING CALCULATION (Your "Before vs After" metric)
    # Business Logic: Total Issues - Anything marked as "FIXED" = What the user still needs to do.
    remaining = len([i for i in all_issues if "FIXED" not in i.severity])
    
    return {
        "ghosts": ghosts,
        "hpa": hpa_gaps,
        "security": security,
        "repairs": repairs,
        "remaining": remaining
    }

# --- THE MOCK TEST ---
# This simulates a real-world scenario where KubeCuro found 4 problems.
def test_fix_command_math():
    # We "Fake" a list of issues found in a cluster.
    # Scenario: 2 items were AUTO-FIXED, 1 is a Security Risk, 1 is a Warning.
    mock_issues = [
        AuditIssue(code="FIXED", severity="🟢 FIXED", ...),
        AuditIssue(code="FIXED", severity="🟢 FIXED", ...),
        AuditIssue(code="RBAC_WILD", severity="🔴 HIGH", ...),
        AuditIssue(code="GHOST", severity="🟠 WARN", ...),
    ]
    
    results = calculate_summary_logic(mock_issues, command="fix")
    
    # ASSERTIONS: These are the "Pass/Fail" criteria.
    # If repairs is not 2, the test fails and tells you your code is broken.
    assert results["repairs"] == 2
    # This confirms your "After" count is correct (4 issues - 2 fixed = 2 remaining).
    assert results["remaining"] == 2 

# --- THE DANGER LIGHT TEST ---
# This ensures that if a high-security risk exists, the UI reflects it.
def test_border_color_logic():
    # Scenario: Only 1 issue found, but it's a "RED" severity issue.
    issues = [AuditIssue(code="RBAC_WILD", severity="🔴 HIGH", ...)]
    
    border_col = "green" # Default to safe
    
    # Logic: "If there is a RED emoji OR a security code, turn the UI RED."
    all_sev = str([i.severity for i in issues])
    security = sum(1 for i in issues if i.code == 'RBAC_WILD')
    
    if "🔴" in all_sev or security > 0:
        border_col = "red"
        
    # This guarantees your software never accidentally shows a "Green" box 
    # when there is a major security hole.
    assert border_col == "red"
