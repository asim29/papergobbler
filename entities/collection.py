from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _parse_paper_ids(raw: object) -> list[str]:
    if isinstance(raw, list):
        return [str(pid) for pid in raw]
    return []


def _parse_str_dict(raw: object) -> dict[str, str]:
    """Parse a dict[str, str] from JSON, returning empty dict on bad input."""
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    return {}


def _parse_metadata_dict(raw: object) -> dict[str, dict[str, object]]:
    """Parse paper_metadata from JSON, returning empty dict on bad input."""
    if isinstance(raw, dict):
        result: dict[str, dict[str, object]] = {}
        for k, v in raw.items():
            if isinstance(v, dict):
                result[str(k)] = {str(mk): mv for mk, mv in v.items()}
        return result
    return {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Collection:
    """
    A user-defined collection of papers. Persisted as JSON on disk.
    """

    id: str
    name: str
    paper_ids: list[str] = field(default_factory=list)
    paper_titles: dict[str, str] = field(default_factory=dict)
    paper_metadata: dict[str, dict[str, object]] = field(default_factory=dict)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, object]:
        """Serialize to a plain dict for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "paper_ids": self.paper_ids,
            "paper_titles": self.paper_titles,
            "paper_metadata": self.paper_metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> Collection:
        """Reconstruct a Collection from a saved JSON dict."""
        return Collection(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            paper_ids=_parse_paper_ids(data.get("paper_ids")),
            paper_titles=_parse_str_dict(data.get("paper_titles")),
            paper_metadata=_parse_metadata_dict(data.get("paper_metadata")),
            created_at=str(data.get("created_at", _now_iso())),
            updated_at=str(data.get("updated_at", _now_iso())),
        )
