from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Collection:
    """
    Represents a user-defined collection of papers.
    """

    id: str
    name: str
    paper_ids: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
