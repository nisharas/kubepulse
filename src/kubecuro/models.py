from dataclasses import dataclass
from typing import Optional

@dataclass
class AuditIssue:
    code: str      
    severity: str  
    file: str      
    message: str   
    source: str = "Unknown" # Added default to prevent init errors
    fix: str = "Manual Review Required"
    line: Optional[int] = None # Renamed from line_number to line

    def __post_init__(self):
        # Ensure consistent UI presentation
        self.source = self.source.capitalize()
        self.severity = self.severity.strip()

    def is_critical(self) -> bool:
        """Returns True if the issue is marked with a High/Critical emoji."""
        return "🔴" in self.severity or "CRITICAL" in self.severity.upper()

    def to_dict(self):
        """Useful if you ever want to export results to JSON."""
        return {
            "code": self.code,
            "severity": self.severity,
            "file": self.file,
            "message": self.message,
            "fix": self.fix,
            "source": self.source,
            "line": self.line
        }
