from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class UserActivityDTO:
    user_id: int
    first_name: str
    username: Optional[str] = None
    language_code: Optional[str] = "en"
    is_premium: bool = False
    content: Optional[str] = None
    has_links: bool = False
    has_inline_buttons: bool = False
    source: str = "organic"