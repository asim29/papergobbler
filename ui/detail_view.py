"""Paper detail view with full metadata and navigation actions."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from entities import Paper
from src.api import get_citations, get_paper, get_recommendations, get_references
from ui.helpers import add_to_collection, push_view, truncate


@dataclass
class DetailView:
    """A single paper's full detail page."""

    paper_id: str
    paper: Paper | None = None


def render_detail_view(view: DetailView) -> None:
    """Render full paper metadata with navigation actions."""
    from ui.list_view import ListView

    if view.paper is None:
        with st.spinner("Loading paper..."):
            view.paper = get_paper(view.paper_id)

    paper = view.paper

    _ = st.subheader(paper.title or "Untitled")

    authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
    year = str(paper.year) if paper.year is not None else ""
    venue = paper.venue or ""
    meta = " · ".join(p for p in [authors, year, venue] if p)
    if meta:
        _ = st.write(meta)

    if paper.tldr:
        _ = st.info(f"**TL;DR:** {paper.tldr}")

    if paper.abstract:
        _ = st.write(paper.abstract)

    doi = paper.external_ids.get("DOI")
    if doi:
        _ = st.write(f"**DOI:** {doi}")

    cites = paper.citation_count
    refs = paper.reference_count
    _ = st.write(f"**Citations:** {cites} · **References:** {refs}")

    title_short = truncate(paper.title or "Untitled", 40)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add to collection", key="detail_add"):
            add_to_collection(paper)
    with col2:
        if st.button("Find similar", key="detail_sim"):
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

    col3, col4 = st.columns(2)
    with col3:
        if st.button(f"View references ({paper.reference_count})", key="detail_refs"):
            refs, next_offset = get_references(paper.paper_id)
            push_view(
                ListView(
                    source="references",
                    label=f'References of "{title_short}"',
                    paper_id=paper.paper_id,
                    results=refs,
                    next_offset=next_offset,
                )
            )
            st.rerun()
    with col4:
        if st.button(f"View cited by ({paper.citation_count})", key="detail_cits"):
            cits, next_offset = get_citations(paper.paper_id)
            push_view(
                ListView(
                    source="citations",
                    label=f'Cited by "{title_short}"',
                    paper_id=paper.paper_id,
                    results=cits,
                    next_offset=next_offset,
                )
            )
            st.rerun()
