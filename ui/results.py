from typing import cast

import streamlit as st

from entities import Collection, Paper


def abstract_preview(text: str, max_chars: int = 250) -> str:
    """
    Produce a short preview of an abstract.

    Args:
        text (str): Full abstract text.
        max_chars (int): Maximum number of characters to display.

    Returns:
        str: Preview string (with "..." appended if truncated).
    """
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."


def add_paper_to_active_collection(paper: Paper) -> None:
    """
    Add a paper to the currently active collection in session state.

    Args:
        paper (Paper): Paper to add.

    Returns:
        None
    """
    active_id = cast(str | None, st.session_state["active_collection_id"])
    if active_id is None:
        _ = st.warning("Create/select a collection first.")
        return

    collections = cast(list[Collection], st.session_state["collections"])

    for c in collections:
        if c.id != active_id:
            continue
        if paper.paper_id in c.paper_ids:
            _ = st.info("Already in collection.")
            return
        c.paper_ids.append(paper.paper_id)
        _ = st.success("Added to collection.")
        st.rerun()

    _ = st.warning("Active collection not found.")


def render_results(results: list[Paper]) -> None:
    """
    Render a compact list of paper results in Streamlit.

    Args:
        results (list[Paper]): Ranked papers to display.

    Returns:
        None
    """
    _ = st.write(f"{len(results)} result(s)")

    for paper in results:
        _ = st.markdown(f"**{paper.title or 'Untitled'}**")

        authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
        year = str(paper.year) if paper.year is not None else ""
        meta_parts = [authors, year]
        meta = " · ".join(part for part in meta_parts if part)

        if meta:
            _ = st.write(meta)

        if paper.journal:
            _ = st.write(paper.journal)

        if paper.abstract:
            _ = st.write(abstract_preview(paper.abstract))

        with st.expander("Details"):
            if paper.abstract:
                _ = st.write(paper.abstract)

            if paper.doi:
                _ = st.write("DOI:", paper.doi)

            if paper.keywords:
                _ = st.write("Keywords:", ", ".join(paper.keywords))

        if st.button("Add to collection", key=f"add_{paper.paper_id}"):
            add_paper_to_active_collection(paper)

        _ = st.divider()
