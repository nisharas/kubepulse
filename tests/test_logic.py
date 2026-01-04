import subprocess
import sys
import os

def test_ghost_service_detection():
    # We scan the entire SAMPLES directory to give Synapse context
    # so it can see the mismatch between services and deployments.
    sample_dir = "tests/samples/"
    
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", sample_dir],
        capture_output=True,
        text=True
    )

    # Log output to GitHub Actions console if the test fails
    print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")

    # Check for the error code SYN-001 (Ghost Service)
    assert "SYN-001" in result.stdout

def test_healthy_connection():
    # Scan only the valid file to ensure no false positives
    target = "tests/samples/valid_connection.yaml"
    
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", target],
        capture_output=True,
        text=True
    )
    
    # We should NOT see the Ghost Service code here
    assert "SYN-001" not in result.stdout
