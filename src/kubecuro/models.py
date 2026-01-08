from dataclasses import dataclass
from typing import Optional

@dataclass
class AuditIssue:
    code: str      
    severity: str  
    file: str      
    message: str   
    source: str = "Unknown"
    fix: str = "Manual Review Required"
    line: Optional[int] = None

    def __post_init__(self):
        # PRESERVE original values for UI rendering (emojis, formatting)
        self._source = self.source.capitalize()
        self._severity = self.severity.strip()
    
    @property
    def source(self) -> str:
        return self._source
    
    @property
    def severity(self) -> str:
        return self._severity
    
    def is_critical(self) -> bool:
        """Returns True if issue is marked with High/Critical emoji."""
        return "🔴" in self.severity or "HIGH" in self.severity or "CRITICAL" in self.severity
    
    def to_dict(self) -> dict:
        """Export results to JSON."""
        return {
            "code": self.code,
            "severity": self.severity,
            "file": self.file,
            "message": self.message,
            "fix": self.fix,
            "source": self.source,
            "line": self.line
        }
