from dataclasses import dataclass,field
from datetime import datetime

@dataclass
class Case:
    id: int
    title: str
    description: str
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.now)