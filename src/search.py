from __future__ import annotations

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from entities import Paper


def tokenize(query: str) -> list[str]:
    """
    Convert a free-text query into normalized search tokens.

    Args:
        query (str): Raw user search input.

    Returns:
        list[str]: Lowercase alphanumeric tokens extracted from the query.
    """
    return re.findall(r"[a-z0-9]+", query.lower())


def build_search_text(paper: Paper) -> str:
    """
    Flatten a Paper into a single lowercase string for indexing.

    Args:
        paper (Paper): A paper record.

    Returns:
        str: Concatenated lowercase text from searchable fields.
    """
    fields: list[str] = [
        paper.title,
        " ".join(paper.authors),
        str(paper.year) if paper.year is not None else "",
        paper.journal or "",
        paper.abstract or "",
        " ".join(paper.keywords),
        paper.doi or "",
    ]
    return " ".join(fields).lower()


@dataclass(frozen=True)
class SearchIndex:
    """
    Precomputed TF-IDF search index for a collection of papers.

    Attributes:
        vectorizer (TfidfVectorizer): Fitted vectorizer.
        doc_matrix: Sparse TF-IDF matrix for all papers.
        papers (list[Paper]): Original papers aligned with doc_matrix rows.
    """

    vectorizer: TfidfVectorizer
    doc_matrix: object
    papers: list[Paper]


def build_index(papers: list[Paper]) -> SearchIndex:
    """
    Build a TF-IDF index over a collection of papers.

    Args:
        papers (list[Paper]): Papers to index.

    Returns:
        SearchIndex: Precomputed search index for efficient querying.
    """
    texts = [build_search_text(p) for p in papers]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        token_pattern=r"[a-z0-9]+",
        ngram_range=(1, 2),
        min_df=1,
    )

    doc_matrix = vectorizer.fit_transform(texts)

    return SearchIndex(
        vectorizer=vectorizer,
        doc_matrix=doc_matrix,
        papers=papers,
    )


def search_papers(
    index: SearchIndex,
    query: str,
    *,
    k: int | None = None,
) -> list[Paper]:
    """
    Search papers using TF-IDF cosine similarity ranking.

    Behavior:
        - If query is empty: return all papers sorted by year descending.
        - Otherwise: rank papers by cosine similarity, then by year descending,
          then title ascending.
        - Only papers with positive similarity scores are returned.

    Args:
        index (SearchIndex): Precomputed search index.
        query (str): User search query.
        k (int | None): Optional maximum number of results.

    Returns:
        list[Paper]: Ranked matching papers.
    """
    q = query.strip()

    if not q:
        return sorted(
            index.papers,
            key=lambda p: (-(p.year or 0), p.title.lower()),
        )

    query_vector = index.vectorizer.transform([q])
    scores = linear_kernel(query_vector, index.doc_matrix).ravel()

    ranked = sorted(
        enumerate(index.papers),
        key=lambda item: (
            -float(scores[item[0]]),
            -(item[1].year or 0),
            item[1].title.lower(),
        ),
    )

    results = [paper for idx, paper in ranked if scores[idx] > 0]

    return results[:k] if k is not None else results
