"""
--------------------------------------------------------------------------------
AUTHOR:      Nishar A Sunkesala / FixMyK8s
PURPOSE:     The Synapse Engine: Maps cross-resource logic gaps (Fully Expanded).
--------------------------------------------------------------------------------
"""
import os
from typing import List
from ruamel.yaml import YAML

from .models import AuditIssue
from .shield import Shield

class Synapse:
    def __init__(self):
        self.yaml = YAML(typ='safe', pure=True)
        self.producers = []      # Workload metadata
        self.workload_docs = []  # Raw docs for Shield
        self.consumers = []      # Services
        self.ingresses = []      # Ingress objects
        self.configs = []        # ConfigMaps and Secrets
        self.hpas = []           # HPA objects
        self.netpols = []        # NetworkPolicies

    def scan_file(self, file_path: str):
        """Extracts deep metadata and tags origin file for every resource."""
        try:
            fname = os.path.basename(file_path)
            with open(file_path, 'r') as f:
                docs = list(self.yaml.load_all(f))
            
            for doc in docs:
                if not doc or 'kind' not in doc: continue
                
                # Tag origin for reporting
                doc['_origin_file'] = fname
                kind = doc['kind']
                name = doc.get('metadata', {}).get('name', 'unknown')
                ns = doc.get('metadata', {}).get('namespace', 'default')
                spec = doc.get('spec', {})

                # --- 1. Workloads (Producers) ---
                if kind in ['Deployment', 'Pod', 'StatefulSet', 'DaemonSet']:
                    self.workload_docs.append(doc)
                    template = spec.get('template', {}) if kind != 'Pod' else doc
                    labels = template.get('metadata', {}).get('labels', {})
                    pod_spec = template.get('spec', {}) if kind != 'Pod' else spec
                    containers = pod_spec.get('containers', [])
                    
                    container_ports = []
                    probes = []
                    volumes = pod_spec.get('volumes', [])
                    
                    for c in containers:
                        # Collect Ports
                        for p in c.get('ports', []):
                            if p.get('containerPort'): container_ports.append(p.get('containerPort'))
                            if p.get('name'): container_ports.append(p.get('name'))
                        
                        # Collect Probes
                        for p_type in ['livenessProbe', 'readinessProbe', 'startupProbe']:
                            p_data = c.get(p_type)
                            if p_data and 'httpGet' in p_data:
                                probes.append({'type': p_type, 'port': p_data['httpGet'].get('port')})

                    self.producers.append({
                        'name': name, 'kind': kind, 'labels': labels, 'namespace': ns, 
                        'ports': container_ports, 'probes': probes, 'file': fname,
                        'serviceName': spec.get('serviceName'), 'volumes': volumes
                    })

                # --- 2. Services (Consumers) ---
                elif kind == 'Service':
                    self.consumers.append({
                        'name': name, 'namespace': ns, 'file': fname,
                        'selector': spec.get('selector', {}),
                        'ports': spec.get('ports', []),
                        'clusterIP': spec.get('clusterIP')
                    })

                # --- 3. Ingress, HPA, Configs ---
                elif kind == 'Ingress':
                    self.ingresses.append({'name': name, 'namespace': ns, 'file': fname, 'spec': spec})
                elif kind == 'HorizontalPodAutoscaler':
                    self.hpas.append({'name': name, 'file': fname, 'doc': doc})
                elif kind in ['ConfigMap', 'Secret']:
                    self.configs.append({'name': name, 'kind': kind, 'namespace': ns, 'file': fname})
                elif kind == 'NetworkPolicy':
                    self.netpols.append({'name': name, 'file': fname, 'selector': spec.get('podSelector', {})})

        except Exception: pass

    def audit(self) -> List[AuditIssue]:
        """Performs cross-resource analysis."""
        results = []
        shield = Shield()

        # --- AUDIT: Service to Pod Matching ---
        for svc in self.consumers:
            if not svc['selector']: continue
            matches = [p for p in self.producers if all(item in p['labels'].items() for item in svc['selector'].items())]
            if not matches:
                results.append(AuditIssue("Synapse", "GHOST", "🔴 HIGH", svc['file'], 
                    f"Service '{svc['name']}' matches 0 Pods.", "Update Service selector."))

        # --- AUDIT: Ingress to Service Mapping ---
        for ing in self.ingresses:
            rules = ing['spec'].get('rules', [])
            for rule in rules:
                paths = rule.get('http', {}).get('paths', [])
                for path in paths:
                    backend = path.get('backend', {})
                    # Handle both old (serviceName) and new (service.name) Ingress schemas
                    svc_name = backend.get('serviceName') or backend.get('service', {}).get('name')
                    if svc_name:
                        match = next((s for s in self.consumers if s['name'] == svc_name and s['namespace'] == ing['namespace']), None)
                        if not match:
                            results.append(AuditIssue("Synapse", "INGRESS_ORPHAN", "🔴 HIGH", ing['file'], 
                                f"Ingress references non-existent Service '{svc_name}'.", "Create the missing Service."))

        # --- AUDIT: ConfigMap/Secret Volume Existence ---
        for p in self.producers:
            for vol in p.get('volumes', []):
                ref_name = None
                if 'configMap' in vol: ref_name = vol['configMap'].get('name')
                if 'secret' in vol: ref_name = vol['secret'].get('secretName')
                
                if ref_name:
                    exists = any(c['name'] == ref_name and c['namespace'] == p['namespace'] for c in self.configs)
                    if not exists:
                        results.append(AuditIssue("Synapse", "VOL_MISSING", "🟠 MED", p['file'], 
                            f"Workload references missing ConfigMap/Secret '{ref_name}'.", "Verify resource existence."))

        # --- AUDIT: HPA, Probes, and StatefulSets (Existing Logic) ---
        for hpa in self.hpas:
            for err in shield.audit_hpa(hpa['doc'], self.workload_docs):
                results.append(AuditIssue("Shield", "HPA_LOGIC", "🔴 HIGH", hpa['file'], err, "Add resource requests."))

        for p in self.producers:
            for probe in p.get('probes', []):
                if probe['port'] and probe['port'] not in p['ports']:
                    results.append(AuditIssue("Synapse", "PROBE_GAP", "🟠 MED", p['file'], 
                        f"Probe port {probe['port']} not exposed.", "Add containerPort."))

        return results
