from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class NegotiationSession:
    id: str
    scenario: str
    mode: str
    role: Optional[str] = None
    max_rounds: int = 10
    status: str = "in_progress"
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NegotiationMessage:
    id: Optional[str] = None
    session_id: str = ""
    speaker: str = ""
    message: str = ""
    created_at: Optional[str] = None
