"""Semantic Scholar API client."""

from __future__ import annotations

import os
from typing import cast

import requests
from dotenv import load_dotenv

from entities import Paper

_ = load_dotenv()

BASE_URL = "https://api.semanticscholar.org/graph/v1"
RECS_URL = "https://api.semanticscholar.org/recommendations/v1/papers/"
FIELDS = (
    "paperId,title,authors,year,venue,abstract,"
    "citationCount,referenceCount,externalIds,tldr"
)
# tldr is not supported on references/citations/recommendations endpoints
FIELDS_NO_TLDR = (
    "paperId,title,authors,year,venue,abstract,citationCount,referenceCount,externalIds"
)

_session_instance: requests.Session | None = None


class S2ApiError(Exception):
    """Raised when a Semantic Scholar API call fails."""

    status_code: int
    message: str

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"S2 API error {status_code}: {message}")


def _session() -> requests.Session:
    """Lazily create and return a reusable requests session with the API key."""
    global _session_instance  # noqa: PLW0603
    if _session_instance is None:
        _session_instance = requests.Session()
        api_key = os.environ.get("S2_API_KEY")
        if api_key:
            _session_instance.headers["x-api-key"] = api_key
    return _session_instance


def _get(url: str, params: dict[str, str | int] | None = None) -> dict[str, object]:
    """Send a GET request and return parsed JSON. Raises S2ApiError on failure."""
    resp = _session().get(url, params=params)
    if not resp.ok:
        raise S2ApiError(resp.status_code, resp.text)
    return cast(dict[str, object], resp.json())


def _post(
    url: str,
    params: dict[str, str | int] | None = None,
    json_body: dict[str, object] | None = None,
) -> dict[str, object]:
    """Send a POST request and return parsed JSON. Raises S2ApiError on failure."""
    resp = _session().post(url, params=params, json=json_body)
    if not resp.ok:
        raise S2ApiError(resp.status_code, resp.text)
    return cast(dict[str, object], resp.json())


def search_papers(
    query: str, offset: int = 0, limit: int = 10
) -> tuple[list[Paper], int | None]:
    """
    Search for papers by keyword.

    Returns (papers, next_offset). next_offset is None if there are no more pages.
    """
    data = _get(
        f"{BASE_URL}/paper/search",
        params={"query": query, "fields": FIELDS, "offset": offset, "limit": limit},
    )

    raw_papers = data.get("data")
    if not isinstance(raw_papers, list):
        raw_papers = []

    papers: list[Paper] = []
    for item in raw_papers:
        if isinstance(item, dict):
            papers.append(Paper.from_s2_response(item))

    next_offset = data.get("next")
    if isinstance(next_offset, int):
        next_offset = int(next_offset)
    else:
        next_offset = None

    return papers, next_offset


def get_paper(paper_id: str) -> Paper:
    """Fetch a single paper by its Semantic Scholar ID."""
    data = _get(
        f"{BASE_URL}/paper/{paper_id}",
        params={"fields": FIELDS},
    )
    return Paper.from_s2_response(data)


def get_references(
    paper_id: str, offset: int = 0, limit: int = 10
) -> tuple[list[Paper], int | None]:
    """
    Get papers referenced by the given paper.

    Returns (papers, next_offset). next_offset is None if there are no more pages.
    """
    data = _get(
        f"{BASE_URL}/paper/{paper_id}/references",
        params={"fields": FIELDS_NO_TLDR, "offset": offset, "limit": limit},
    )

    raw_items = data.get("data")
    if not isinstance(raw_items, list):
        raw_items = []

    papers: list[Paper] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        cited = item.get("citedPaper")
        if not isinstance(cited, dict):
            continue
        if not cited.get("paperId"):
            continue
        papers.append(Paper.from_s2_response(cited))

    next_offset = data.get("next")
    if isinstance(next_offset, int):
        next_offset = int(next_offset)
    else:
        next_offset = None

    return papers, next_offset


def get_citations(
    paper_id: str, offset: int = 0, limit: int = 10
) -> tuple[list[Paper], int | None]:
    """
    Get papers that cite the given paper.

    Returns (papers, next_offset). next_offset is None if there are no more pages.
    """
    data = _get(
        f"{BASE_URL}/paper/{paper_id}/citations",
        params={"fields": FIELDS_NO_TLDR, "offset": offset, "limit": limit},
    )

    raw_items = data.get("data")
    if not isinstance(raw_items, list):
        raw_items = []

    papers: list[Paper] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        citing = item.get("citingPaper")
        if not isinstance(citing, dict):
            continue
        if not citing.get("paperId"):
            continue
        papers.append(Paper.from_s2_response(citing))

    next_offset = data.get("next")
    if isinstance(next_offset, int):
        next_offset = int(next_offset)
    else:
        next_offset = None

    return papers, next_offset


def get_recommendations(paper_id: str, limit: int = 10) -> list[Paper]:
    """
    Get paper recommendations based on a seed paper.

    No pagination — use limit to control result size (max 500).
    """
    data = _post(
        RECS_URL,
        params={"fields": FIELDS_NO_TLDR, "limit": limit},
        json_body={"positivePaperIds": [paper_id]},
    )

    raw_papers = data.get("recommendedPapers")
    if not isinstance(raw_papers, list):
        raw_papers = []

    papers: list[Paper] = []
    for item in raw_papers:
        if isinstance(item, dict) and item.get("paperId"):
            papers.append(Paper.from_s2_response(item))

    return papers
