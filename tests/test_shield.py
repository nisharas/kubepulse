import pytest
from kubecuro.shield import Shield

@pytest.fixture
def shield_engine():
    return Shield()

def test_rbac_wildcard_detection(shield_engine):
    """Verify that global wildcards in RBAC are flagged as 🔴 HIGH"""
    bad_rbac = {
        "kind": "ClusterRole",
        "metadata": {"name": "star-lord"},
        "rules": [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]
    }
    findings = shield_engine.check_rbac_security(bad_rbac)
    assert any(f['code'] == "RBAC_WILD" and f['severity'] == "🔴 HIGH" for f in findings)

def test_privileged_container_detection(shield_engine):
    """Verify that privileged containers are flagged"""
    bad_pod = {
        "kind": "Pod",
        "metadata": {"name": "unsafe-pod"},
        "spec": {
            "containers": [{
                "name": "hacker-tool",
                "securityContext": {"privileged": True}
            }]
        }
    }
    findings = shield_engine.check_version_and_security(bad_pod)
    assert any(f['code'] == "SEC_PRIVILEGED" for f in findings)

def test_hpa_missing_requests(shield_engine):
    """Verify HPA flags missing requests in the target deployment"""
    # Simulate the 'web-stack.yaml' logic
    deployment = {
        "kind": "Deployment",
        "metadata": {"name": "web-deploy"},
        "spec": {"template": {"spec": {"containers": [{"name": "app", "resources": {}}]}}}
    }
    hpa = {
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": "web-hpa"},
        "spec": {
            "scaleTargetRef": {"name": "web-deploy"},
            "metrics": [{"type": "Resource", "resource": {"name": "cpu"}}]
        }
    }
    
    # We pass the deployment in the all_docs list
    findings = shield_engine.audit_hpa(hpa, workload_docs=[deployment])
    assert any(f['code'] == "HPA_MISSING_REQ" for f in findings)
