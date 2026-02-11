import re

from .entities import Paper

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
    Flatten a Paper into a single lowercase string for simple matching.

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


def score_paper(search_text: str, tokens: list[str]) -> int:
    """
    Compute a simple relevance score based on token occurrence counts.

    Args:
        search_text (str): Flattened searchable text.
        tokens (list[str]): Query tokens.

    Returns:
        int: Total occurrences of tokens in the search text.
    """
    return sum(search_text.count(token) for token in tokens)


def search_papers(papers: list[Paper], query: str) -> list[Paper]:
    """
    Search papers using AND token matching over flattened text.

    Behavior:
        - If query is empty: return all papers sorted by year descending.
        - Otherwise: keep papers where all tokens appear and rank by
          score descending, then year descending, then title ascending.

    Args:
        papers (list[Paper]): Papers to search.
        query (str): User search query.

    Returns:
        list[Paper]: Ranked matching papers.
    """
    tokens = tokenize(query)

    results: list[tuple[int, Paper]] = []

    for paper in papers:
        text = build_search_text(paper)

        if tokens:
            if not all(token in text for token in tokens):
                continue
            score = score_paper(text, tokens)
        else:
            score = 0

        results.append((score, paper))

    results.sort(
        key=lambda item: (
            -item[0],
            -(item[1].year or 0),
            item[1].title.lower(),
        )
    )

    return [paper for _, paper in results]
