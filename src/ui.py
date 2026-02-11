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
    Render sidebar navigation + collections + items list.

    Args:
        papers (list[Paper]): All papers (for mapping paper_id -> Paper).

    Returns:
        None
    """
    collections = cast(list[Collection], st.session_state["collections"])
    active_id = cast(str | None, st.session_state["active_collection_id"])
    selected_id = cast(str | None, st.session_state["selected_paper_id"])

    by_id = {p.paper_id: p for p in papers}

    # ---- Nav ----
    if st.sidebar.button("Search", key="nav_search"):
        st.session_state["page"] = "search"
        st.rerun()

    _ = st.sidebar.divider()

    # ---- Collections ----
    _ = st.sidebar.header("Collections")

    new_name: str = st.sidebar.text_input(
        "New collection name", key="new_collection_name"
    )
    if st.sidebar.button("Create collection", key="create_collection"):
        name = new_name.strip()
        if not name:
            _ = st.sidebar.error("Enter a name.")
        else:
            cid = hashlib.sha1(name.encode("utf-8")).hexdigest()
            if any(c.id == cid for c in collections):
                _ = st.sidebar.warning("Collection already exists.")
            else:
                collections.append(Collection(id=cid, name=name))
                st.session_state["active_collection_id"] = cid
                st.rerun()

    if not collections:
        _ = st.sidebar.caption("No collections yet.")
        return

    # Clickable collections list
    names = [c.name for c in collections]
    active = next((c for c in collections if c.id == active_id), None)
    default_idx = 0 if active is None else names.index(active.name)

    picked = st.sidebar.selectbox("Collections", names, index=default_idx)
    picked_col = next(c for c in collections if c.name == picked)

    st.session_state["active_collection_id"] = picked_col.id

    _ = st.sidebar.divider()

    # ---- Items (active collection) ----
    active = next((c for c in collections if c.id == active_id), None)
    if active is None:
        _ = st.sidebar.caption("Select a collection to see items.")
        return

    if st.sidebar.button(
        f"{active.name} ({len(active.paper_ids)})", key="open_active_collection"
    ):
        st.session_state["page"] = "collection"
        st.rerun()

    if not active.paper_ids:
        _ = st.sidebar.caption("Empty.")
        return

    for pid in active.paper_ids:
        p = by_id.get(pid)
        title = p.title if p is not None and p.title else "(missing)"
        prefix = "• "
        if pid == selected_id:
            prefix = "→ "
        if st.sidebar.button(f"{prefix}{title}", key=f"item_{pid}"):
            st.session_state["selected_paper_id"] = pid
            st.rerun()


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
