#!/usr/bin/env python3
"""
--------------------------------------------------------------------------------
AUTHOR:      Nishar A Sunkesala / FixMyK8s
PURPOSE:      The Healer Engine: Syntax Repair, API Migration, & Security Patching.
--------------------------------------------------------------------------------
"""
import sys
import re
import difflib
import os
from io import StringIO
from ruamel.yaml import YAML

# Import Shield to ensure we use the same deprecation map
try:
    from .shield import Shield
except ImportError:
    from shield import Shield

class Healer:
    def __init__(self):
        # Round-trip loader preserves comments and block styles
        self.yaml = YAML(typ='rt')
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.preserve_quotes = True
        self.shield = Shield()

    def apply_security_patches(self, doc, kind):
        """
        Injects security best practices and stability fixes into the YAML object.
        """
        if kind in ['Deployment', 'Pod', 'StatefulSet', 'DaemonSet']:
            spec = doc.get('spec', {})
            # Navigate to the Pod Spec (Workload vs Bare Pod)
            template = spec.get('template', {}) if kind != 'Pod' else doc
            t_spec = template.get('spec')

            if t_spec is not None:
                # 1. FIX: Automount ServiceAccount Token
                # Best practice: if not specified, set to False to reduce attack surface
                if t_spec.get('automountServiceAccountToken') is None:
                    t_spec['automountServiceAccountToken'] = False
                
                # 2. FIX: Privileged Mode
                # If a container is found with privileged: true, we reset it for safety
                containers = t_spec.get('containers', [])
                for c in containers:
                    s_ctx = c.get('securityContext')
                    if s_ctx and s_ctx.get('privileged') is True:
                        s_ctx['privileged'] = False

    def heal_file(self, file_path, apply_fixes=True, dry_run=False, return_content=False):
        """
        The main healing pipeline: Regex -> API Upgrade -> Security Injection.
        """
        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'r') as f:
                original_content = f.read()

            # Split multi-manifest files safely
            raw_docs = re.split(r'^---', original_content, flags=re.MULTILINE)
            healed_parts = []

            for doc_str in raw_docs:
                if not doc_str.strip():
                    continue

                # --- Phase 1: Regex Syntax Repair ---
                # Fix missing colons at end of lines
                d = re.sub(r'^(?![ \t]*#)([ \t]*[\w.-]+)(?=[ \t]*$)', r'\1:', doc_str, flags=re.MULTILINE)
                # Fix missing space after colon
                d = re.sub(r'(^[ \t]*[\w.-]+):(?!\s| )', r'\1: ', d, flags=re.MULTILINE)
                # Tabs to Spaces conversion
                d = d.replace('\t', '    ')

                try:
                    parsed = self.yaml.load(d)
                    if parsed and apply_fixes:
                        kind = parsed.get('kind')
                        api = parsed.get('apiVersion')

                        # --- Phase 2: API Version Migration ---
                        if api in self.shield.DEPRECATIONS:
                            mapping = self.shield.DEPRECATIONS[api]
                            new_api = mapping.get(kind, mapping.get("default")) if isinstance(mapping, dict) else mapping
                            
                            if new_api and not str(new_api).startswith("REMOVED"):
                                parsed['apiVersion'] = new_api

                        # --- Phase 3: Security & Stability Patching ---
                        self.apply_security_patches(parsed, kind)

                    if parsed:
                        buf = StringIO()
                        self.yaml.dump(parsed, buf)
                        healed_parts.append(buf.getvalue().strip())
                
                except Exception:
                    # If YAML logic fails, keep the regex-cleaned string as fallback
                    healed_parts.append(d.strip())

            # Reconstruct the file with clean separators
            healed_final = "---\n" + "\n---\n".join(healed_parts) + "\n"

            # Check for actual changes using diff
            diff = list(difflib.unified_diff(
                original_content.splitlines(),
                healed_final.splitlines(),
                lineterm=''
            ))

            if not diff:
                return False 

            if return_content:
                return healed_final
            
            if not dry_run:
                with open(file_path, 'w') as f:
                    f.write(healed_final)
                return True
            
            return True # Logic changed, but skipped write due to dry-run

        except Exception as e:
            return False

def linter_engine(file_path, apply_api_fixes=True, dry_run=False, return_content=False):
    """Bridge for main.py integration."""
    h = Healer()
    return h.heal_file(file_path, apply_api_fixes, dry_run, return_content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: healer.py <file.yaml>")
    else:
        if linter_engine(sys.argv[1]):
            print(f"✅ Healed {sys.argv[1]}")
        else:
            print(f"ℹ️ No changes required for {sys.argv[1]}")
