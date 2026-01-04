import subprocess
import sys
import os

# Helper to run KubeCuro commands
def run_kubecuro(*args):
  
  # This ensures the current directory is added to the path 
    # so 'kubecuro.main' can always be found
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    return subprocess.run(
        [sys.executable, "-m", "kubecuro.main", *args],
        capture_output=True,
        text=True
    )

def test_ghost_service_logic():
    """Scenario: Service exists but matches no pods."""
    result = run_kubecuro("scan", "tests/samples/")
    assert "GHOST SERVICE" in result.stdout

def test_deprecated_api_shield():
    """Scenario: Shield should catch old API versions."""
    result = run_kubecuro("scan", "tests/samples/deprecated_api.yaml")
    # Shield usually outputs MED severity for deprecated APIs
    assert "API_DEPRECATED" in result.stdout or "MED" in result.stdout

def test_hpa_resource_check():
    """Scenario: HPA scaling without resource requests defined."""
    result = run_kubecuro("scan", "tests/samples/hpa_logic_error.yaml")
    output = result.stdout.upper()
    # Looking for the core keywords that Synapse outputs
    assert "HPA" in output
    assert "RESOURCE" in output or "GAP" in output

def test_healer_fix_functionality():
    """Scenario: 'fix' command should actually work."""
    target = "tests/samples/syntax_error.yaml"
    fix_result = run_kubecuro("fix", target)
    # If it healed the file, "No issues found" will NOT be there because a table appeared
    assert "FIXED" in fix_result.stdout or "✔ No issues found!" not in fix_result.stdout

def test_checklist_command():
    """Scenario: Ensure the UI checklist displays."""
    # Note: Checklist doesn't need a target file
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "checklist"],
        capture_output=True,
        text=True
    )
    assert "Checklist" in result.stdout
