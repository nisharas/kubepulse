import subprocess
import pytest

def test_ghost_service_detection():
    """
    Test that Kubecuro correctly identifies a 'Ghost Service' 
    (A Service with no matching Pod).
    """
    # Changed "check" to "scan" to match the actual tool command
    result = subprocess.run(
        ["kubecuro", "scan", "tests/samples/ghost_service_error.yaml"],
        capture_output=True,
        text=True
    )
    
    # We expect to see the logic ID SYN-001 in the output
    assert "SYN-001" in result.stdout
    assert "Ghost Service" in result.stdout

def test_healthy_connection():
    """
    Test that Kubecuro does NOT report errors for a 
    perfectly connected Service and Pod.
    """
    # Changed "check" to "scan"
    result = subprocess.run(
        ["kubecuro", "scan", "tests/samples/valid_connection.yaml"],
        capture_output=True,
        text=True
    )
    
    # We expect the output to confirm no issues were found
    # (Note: Check your tool's actual success message, it might be 'No issues found')
    assert "SYN-001" not in result.stdout
