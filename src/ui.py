import hashlib
from typing import cast

import streamlit as st

from .entities import Collection, Paper


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


def render_active_collection(papers: list[Paper]) -> None:
    """
    Render the currently active collection in the sidebar.

    Args:
        papers (list[Paper]): All papers (used to map paper_id -> Paper).

    Returns:
        None
    """
    collections = cast(list[Collection], st.session_state["collections"])
    active_id = cast(str | None, st.session_state["active_collection_id"])

    if active_id is None:
        _ = st.sidebar.caption("No active collection.")
        return

    active = next((c for c in collections if c.id == active_id), None)
    if active is None:
        _ = st.sidebar.caption("Active collection not found.")
        return

    by_id = {p.paper_id: p for p in papers}

    _ = st.sidebar.subheader(f"Items ({len(active.paper_ids)})")

    if not active.paper_ids:
        _ = st.sidebar.caption("Empty.")
        return

    for pid in active.paper_ids:
        p = by_id.get(pid)
        title = p.title if p is not None and p.title else "(missing)"
        _ = st.sidebar.write(f"• {title}")


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


def render_sidebar(papers: list[Paper]) -> None:
    """
    Render sidebar UI for creating/selecting collections and viewing contents.

    Uses:
        st.session_state["collections"]: list[Collection]
        st.session_state["active_collection_id"]: str | None

    Args:
        papers (list[Paper]): All papers (used for rendering collection contents).

    Returns:
        None
    """
    _ = st.sidebar.header("Collections")

    new_name: str = st.sidebar.text_input(
        "New collection name", key="new_collection_name"
    )

    if st.sidebar.button("Create collection"):
        name = new_name.strip()
        if not name:
            _ = st.sidebar.error("Enter a name.")
            return

        cid = hashlib.sha1(name.strip().encode("utf-8")).hexdigest()

        collections = cast(list[Collection], st.session_state["collections"])
        if any(c.id == cid for c in collections):
            _ = st.sidebar.warning("Collection already exists.")
            return

        collections.append(Collection(id=cid, name=name))
        st.session_state["active_collection_id"] = cid
        _ = st.sidebar.success("Created.")
        st.rerun()

    collections = cast(list[Collection], st.session_state["collections"])
    if not collections:
        _ = st.sidebar.info("No collections yet.")
        return

    # Pick active
    id_by_name = {c.name: c.id for c in collections}
    names = list(id_by_name.keys())

    active_id = cast(str | None, st.session_state["active_collection_id"])
    idx = 0
    if active_id is not None:
        ids = list(id_by_name.values())
        if active_id in ids:
            idx = ids.index(active_id)

    active_name = st.sidebar.selectbox("Active collection", names, index=idx)
    st.session_state["active_collection_id"] = id_by_name[active_name]

    _ = st.sidebar.divider()
    render_active_collection(papers)
