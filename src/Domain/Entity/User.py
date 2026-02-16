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
    warnings: int = 0

    def is_spamming(self, threshold_seconds: int) -> bool:
        time_delta = (datetime.now() - self.last_seen).total_seconds()
        return time_delta < threshold_seconds
    
    def add_warning(self):
        self.warnings += 1

    def reset_warnings(self):
        self.warnings = 0


    def record_activity(self):
        self.message_count += 1
        self.last_seen = datetime.now()
    
    @property
    def display_name(self) -> str:
        return f"@{self.username}" if self.username else self.first_name