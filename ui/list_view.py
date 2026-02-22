"""Unified list view for search results, references, citations, and similar papers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import streamlit as st

from entities import Paper
from src.api import (
    get_citations,
    get_recommendations,
    get_references,
    search_papers,
)
from ui.helpers import add_to_collection, push_view, truncate


@dataclass
class ListView:
    """A paginated list of papers from a single source."""

    source: Literal["search", "references", "citations", "similar"]
    label: str
    query: str | None = None
    paper_id: str | None = None
    results: list[Paper] = field(default_factory=list)
    next_offset: int | None = None


def _load_more(view: ListView) -> None:
    """Fetch the next page and append results."""
    if view.next_offset is None:
        return

    if view.source == "search" and view.query is not None:
        papers, next_offset = search_papers(view.query, offset=view.next_offset)
    elif view.source == "references" and view.paper_id is not None:
        papers, next_offset = get_references(view.paper_id, offset=view.next_offset)
    elif view.source == "citations" and view.paper_id is not None:
        papers, next_offset = get_citations(view.paper_id, offset=view.next_offset)
    else:
        return

    view.results.extend(papers)
    view.next_offset = next_offset


def render_list_view(view: ListView) -> None:
    """Render a list of paper cards with navigation actions."""
    from ui.detail_view import DetailView

    _ = st.caption(view.label)

    if not view.results:
        _ = st.info("No results.")
        return

    for i, paper in enumerate(view.results):
        if st.button(f"**{paper.title or 'Untitled'}**", key=f"title_{i}"):
            push_view(DetailView(paper_id=paper.paper_id, paper=paper))
            st.rerun()

        authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
        year = str(paper.year) if paper.year is not None else ""
        venue = paper.venue or ""
        meta = " · ".join(p for p in [authors, year, venue] if p)
        if meta:
            _ = st.write(meta)

        if paper.abstract:
            _ = st.write(truncate(paper.abstract))

        _ = st.write(f"Citations: {paper.citation_count}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add to collection", key=f"add_{i}"):
                add_to_collection(paper)
        with col2:
            if st.button("Find similar", key=f"sim_{i}"):
                title_short = truncate(paper.title or "Untitled", 40)
                recs = get_recommendations(paper.paper_id)
                push_view(
                    ListView(
                        source="similar",
                        label=f'Similar to "{title_short}"',
                        paper_id=paper.paper_id,
                        results=recs,
                    )
                )
                st.rerun()

        _ = st.divider()

    if view.next_offset is not None:
        if st.button("Load more", key="load_more"):
            _load_more(view)
            st.rerun()
