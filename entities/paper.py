import hashlib
from dataclasses import dataclass
from typing import cast

JSONDict = dict[str, object]


def make_paper_id(title: str, year: int | None, authors: list[str]) -> str:
    """
    Create a stable ID for a paper using a short SHA-1 hash.

    Args:
        title (str): Paper title.
        year (int | None): Publication year.
        authors (list[str]): Author names.

    Returns:
        str: Stable 12-char hexadecimal identifier.
    """
    first_author = authors[0] if authors else ""
    base = f"{title.strip().lower()}|{year or ''}|{first_author.strip().lower()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Paper:
    """
    Represents a single research paper in the system.
    """

    id: int
    paper_id: str
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

        # ---- final id for database ----
        stable_id = make_paper_id(title=title, year=year, authors=authors)

        return Paper(
            id=paper_id,
            paper_id=stable_id,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            keywords=keywords,
            doi=doi,
        )
