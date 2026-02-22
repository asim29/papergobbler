from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import cast

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


@dataclass(frozen=True)
class Paper:
    """
    A research paper sourced from Semantic Scholar.
    """

    paper_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    citation_count: int = 0
    reference_count: int = 0
    external_ids: dict[str, str] = field(default_factory=dict)
    tldr: str | None = None

    @property
    def citekey(self) -> str:
        """
        Generate a BibTeX-style cite key: lastNameYearShortTitle.

        E.g. "vaswani2017AttentionAll" for Vaswani et al. 2017,
        "Attention Is All You Need".
        """
        # Last name of first author
        if self.authors:
            last = self.authors[0].split()[-1]
            last = re.sub(r"[^a-z]", "", last.lower())
        else:
            last = "anon"

        year = str(self.year) if self.year else ""

        # First three non-stopword words from the title, each capitalized
        words = cast("list[str]", re.findall(r"[a-zA-Z]+", self.title))
        filtered = [w for w in words if w.lower() not in ENGLISH_STOP_WORDS]
        short = "".join(w.capitalize() for w in filtered[:3])

        return f"{last}{year}{short}"

    @staticmethod
    def from_s2_response(data: dict[str, object]) -> Paper:
        """
        Parse a Semantic Scholar API paper object into a Paper.

        Handles the S2 response shape:
        - authors: [{"authorId": "...", "name": "..."}]
        - externalIds: {"DOI": "...", "ArXiv": "...", ...} (nulls possible)
        - tldr: {"model": "...", "text": "..."} or null
        """
        paper_id = data.get("paperId")
        if not isinstance(paper_id, str) or not paper_id:
            msg = f"Missing or invalid paperId: {data.get('paperId')!r}"
            raise ValueError(msg)

        title = data.get("title") or ""
        if isinstance(title, str):
            title = title.strip()
        else:
            title = ""

        # Flatten authors from [{"authorId": "...", "name": "..."}] to ["name"]
        raw_authors = data.get("authors")
        authors: list[str] = []
        if isinstance(raw_authors, list):
            for a in raw_authors:
                if isinstance(a, dict):
                    name = a.get("name")
                    if isinstance(name, str) and name.strip():
                        authors.append(name.strip())
        else:
            authors = []

        year = data.get("year")
        if isinstance(year, int):
            year = int(year)
        else:
            year = None

        venue = data.get("venue")
        if isinstance(venue, str):
            venue = venue.strip() or None
        else:
            venue = None

        abstract = data.get("abstract")
        if isinstance(abstract, str):
            abstract = abstract.strip() or None
        else:
            abstract = None

        citation_count = data.get("citationCount")
        if isinstance(citation_count, int):
            citation_count = int(citation_count)
        else:
            citation_count = 0

        reference_count = data.get("referenceCount")
        if isinstance(reference_count, int):
            reference_count = int(reference_count)
        else:
            reference_count = 0

        # Filter out null values from externalIds
        raw_ext = data.get("externalIds")
        external_ids: dict[str, str] = {}
        if isinstance(raw_ext, dict):
            for k, v in raw_ext.items():
                if isinstance(v, str):
                    external_ids[k] = v
                elif isinstance(v, int):
                    external_ids[k] = str(v)
        else:
            external_ids = {}

        # Extract tldr text from {"model": "...", "text": "..."}
        raw_tldr = data.get("tldr")
        tldr: str | None = None
        if isinstance(raw_tldr, dict):
            tldr_text = raw_tldr.get("text")
            if isinstance(tldr_text, str) and tldr_text.strip():
                tldr = tldr_text.strip()
            else:
                tldr = None
        else:
            tldr = None

        return Paper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            abstract=abstract,
            citation_count=citation_count,
            reference_count=reference_count,
            external_ids=external_ids,
            tldr=tldr,
        )
