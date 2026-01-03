@dataclass
class AuditIssue:
    code: str      
    severity: str  
    file: str      
    message: str   
    fix: str       
    source: str    
    line_number: Optional[int] = None 

    def __post_init__(self):
        self.source = self.source.capitalize()

    def is_critical(self) -> bool:
        return "🔴" in self.severity
