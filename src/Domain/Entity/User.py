from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    first_name: str
    
    username: Optional[str] = None
    message_count: int = 0
    last_seen: datetime = field(default_factory=datetime.now)

    def record_activity(self):
        self.message_count += 1
        self.last_seen = datetime.now()
    
    @property
    def display_name(self) -> str:
        return f"@{self.username}" if self.username else self.first_name