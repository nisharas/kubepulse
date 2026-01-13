import re

class RawLexer:
    """
    Pass 1: Character-level repair.
    Fixes spacing around colons and cleans up malformed key-value pairs.
    """
    
    def __init__(self):
        # Pattern to find the first colon that isn't inside a comment or quoted string
        # This protects things like "nginx:latest" if it's properly quoted.
        self.kv_pattern = re.compile(r'^(\s*)([^#:"\']+)\s*:\s*(.*)$')

    def repair_line(self, line: str) -> str:
        # 1. Preserve empty lines or comment-only lines
        if not line.strip() or line.strip().startswith('#'):
            return line

        # 2. Extract indentation, key, and value
        match = self.kv_pattern.match(line)
        if match:
            indent = match.group(1)
            key = match.group(2).strip()
            value = match.group(3).strip()

            # Normalize: Ensure exactly one space after colon, zero before.
            # Fixes: 'kind:Pod' -> 'kind: Pod'
            # Fixes: 'metadata  :' -> 'metadata:'
            # Fixes: 'apiVersion:   v1' -> 'apiVersion: v1'
            if value:
                return f"{indent}{key}: {value}"
            else:
                return f"{indent}{key}:"
        
        # 3. If no match (e.g., a list item like "- name: app"), 
        # we still want to clean up trailing whitespace.
        return line.rstrip()

    def process_string(self, raw_yaml: str) -> str:
        lines = raw_yaml.splitlines()
        repaired_lines = [self.repair_line(line) for line in lines]
        return "\n".join(repaired_lines)
