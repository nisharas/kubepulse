from dataclasses import dataclass
from typing import Optional

@dataclass
class AuditIssue:
    """Production-grade audit issue model."""
    # ✅ Required fields FIRST
    code: str
    file: str
    # ✅ Optional fields LAST (fixes pytest error)
    line: Optional[int] = None
    severity: str = "🟢 LOW"
    message: str = ""
    
    def is_critical(self) -> bool:
        """Check if issue is critical."""
        return "🔴" in self.severity or "HIGH" in self.severity or "CRITICAL" in self.severity
    
    def to_dict(self) -> dict:
        """Export for JSON/baseline."""
        return {
            "code": self.code,
            "file": self.file,
            "line": self.line,
            "severity": self.severity,
            "message": self.message
        }
