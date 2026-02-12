import streamlit as st

from entities import Paper


def render_paper_view(paper: Paper) -> None:
    """
    Render a focused view of a single paper.

    Args:
        paper (Paper): Paper to render.

    Returns:
        None
    """
    _ = st.subheader(paper.title or "Untitled")

    authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
    year = str(paper.year) if paper.year is not None else ""
    meta = " · ".join([p for p in [authors, year] if p])
    if meta:
        _ = st.write(meta)

    if paper.journal:
        _ = st.write(paper.journal)

    if paper.abstract:
        _ = st.write(paper.abstract)

    if paper.doi:
        _ = st.write("DOI:", paper.doi)

    if paper.keywords:
        _ = st.write("Keywords:", ", ".join(paper.keywords))
