from dataclasses import dataclass
from typing import Optional

@dataclass(frozen = True)
class TelegramProfile:
    username        : Optional[str] = None
    language_code   : Optional[str] = None
    is_premium      : bool = False
    source          : str = "organic"