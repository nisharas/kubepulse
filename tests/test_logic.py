import subprocess
import sys

def test_ghost_service_detection():
    # We run the module directly. Since we installed it with 'pip install .',
    # Python will find it in the official site-packages automatically.
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", "tests/samples/ghost_service_error.yaml"],
        capture_output=True,
        text=True
    )

    # Useful for debugging if it fails
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

    assert "SYN-001" in result.stdout

def test_healthy_connection():
    result = subprocess.run(
        [sys.executable, "-m", "kubecuro.main", "scan", "tests/samples/valid_connection.yaml"],
        capture_output=True,
        text=True
    )
    assert "SYN-001" not in result.stdout
