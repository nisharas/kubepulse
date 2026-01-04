import subprocess
import sys
import os

def test_ghost_service_detection():
    # Force the sub-process to use the same "library path" as the current test
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(sys.path)

    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", "tests/samples/ghost_service_error.yaml"],
        capture_output=True,
        text=True,
        env=env  # <--- This is the key! It passes the "Clean Room" settings through.
    )

    assert "SYN-001" in result.stdout

def test_healthy_connection():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", "tests/samples/valid_connection.yaml"],
        capture_output=True,
        text=True,
        env=env
    )
    assert "SYN-001" not in result.stdout
