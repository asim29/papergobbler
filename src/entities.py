from dataclasses import dataclass
from typing import cast


JSONDict = dict[str, object]


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
    def from_dict(data: JSONDict) -> "Paper":
        """
        Create a Paper instance from a raw JSON dictionary.

        Args:
            data (JSONDict): A single paper dictionary from the dataset.

        Returns:
            Paper: A normalized Paper instance.
        """
        # ---- id ----
        raw_id = data.get("id")
        paper_id = int(raw_id) if isinstance(raw_id, int) else -1

        # ---- title ----
        raw_title = data.get("title")
        title = raw_title.strip() if isinstance(raw_title, str) else ""

        # ---- year ----
        raw_year = data.get("year")
        year = int(raw_year) if isinstance(raw_year, int) else None

        # ---- journal / abstract / doi ----
        raw_journal = data.get("journal")
        journal = raw_journal.strip() or None if isinstance(raw_journal, str) else None

        raw_abstract = data.get("abstract")
        abstract = (
            raw_abstract.strip() or None if isinstance(raw_abstract, str) else None
        )

        raw_doi = data.get("doi")
        doi = raw_doi.strip() or None if isinstance(raw_doi, str) else None

        # ---- authors ----
        raw_authors = data.get("authors")
        authors_list = (
            cast(list[object], raw_authors) if isinstance(raw_authors, list) else []
        )
        authors: list[str] = []
        for a in authors_list:
            if isinstance(a, str):
                s = a.strip()
                if s:
                    authors.append(s)

        # ---- keywords ----
        raw_keywords = data.get("keywords")
        keywords_list = (
            cast(list[object], raw_keywords) if isinstance(raw_keywords, list) else []
        )
        keywords: list[str] = []
        for k in keywords_list:
            if isinstance(k, str):
                s = k.strip()
                if s:
                    keywords.append(s)

        return Paper(
            id=paper_id,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            keywords=keywords,
            doi=doi,
        )
