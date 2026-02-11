from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Paper:
    """
    Represents a single research paper in the system.
    """

    id: int
    title: str
    authors: list[str]
    year: int | None
    journal: str | None
    abstract: str | None
    keywords: list[str]
    doi: str | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Paper":
        """
        Create a Paper instance from a raw JSON dictionary.

        Args:
            data (dict[str, Any]): A single paper dictionary from the dataset.

        Returns:
            Paper: A normalized Paper instance.
        """
        authors_raw = data.get("authors") or []
        keywords_raw = data.get("keywords") or []

        return Paper(
            id=int(data.get("id", -1)),
            title=str(data.get("title", "")).strip(),
            authors=[str(a).strip() for a in authors_raw if str(a).strip()],
            year=int(data["year"]) if data.get("year") is not None else None,
            journal=(str(data.get("journal", "")).strip() or None),
            abstract=(str(data.get("abstract", "")).strip() or None),
            keywords=[str(k).strip() for k in keywords_raw if str(k).strip()],
            doi=(str(data.get("doi", "")).strip() or None),
        )
