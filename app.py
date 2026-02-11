from pathlib import Path
from typing import cast

import streamlit as st

from src.db import load_papers
from src.entities import Paper, Collection
from src.search import SearchIndex, build_index, search_papers
from src.ui import render_results, render_sidebar, render_paper_view

DATA_PATH = Path(__file__).parent / "data" / "papers.json"


def init_state() -> None:
    """
    Initialize Streamlit session state for collections and selection.
    """
    if "collections" not in st.session_state:
        st.session_state["collections"] = []  # list[Collection]

    if "active_collection_id" not in st.session_state:
        st.session_state["active_collection_id"] = None  # str | None

    if "results" not in st.session_state:
        st.session_state["results"] = []  # list[Paper]

    if "has_searched" not in st.session_state:
        st.session_state["has_searched"] = False

    if "page" not in st.session_state:
        st.session_state["page"] = "search"  # "search" | "collection"

    if "selected_paper_id" not in st.session_state:
        st.session_state["selected_paper_id"] = None  # str | None


@st.cache_data
def cached_load_papers(path: Path) -> list[Paper]:
    """
    Load papers with Streamlit caching enabled.

    Args:
        path (Path): Path to the JSON dataset.

    Returns:
        list[Paper]: Loaded paper entities.
    """
    return load_papers(path)


@st.cache_resource
def cached_build_index(papers: list[Paper]) -> SearchIndex:
    """
    Build the TF-IDF search index with Streamlit resource caching enabled.

    Args:
        papers (list[Paper]): Papers to index.

    Returns:
        SearchIndex: Precomputed TF-IDF index.
    """
    return build_index(papers)


def main() -> None:
    """
    Streamlit application entrypoint.
    """
    _ = st.title("Literature Search")

    papers: list[Paper] = cached_load_papers(DATA_PATH)
    index: SearchIndex = cached_build_index(papers)

    init_state()
    render_sidebar(papers)

    page = cast(str, st.session_state["page"])
    selected_id = cast(str | None, st.session_state["selected_paper_id"])

    by_id: dict[str, Paper] = {p.paper_id: p for p in papers}
    collections = cast(list[Collection], st.session_state["collections"])
    active_cid = cast(str | None, st.session_state["active_collection_id"])
    active = next((c for c in collections if c.id == active_cid), None)

    if page == "search":
        query: str = st.text_input("Search")

        if st.button("Search"):
            st.session_state["results"] = search_papers(index, query)
            st.session_state["has_searched"] = True

        if cast(bool, st.session_state["has_searched"]):
            results = cast(list[Paper], st.session_state["results"])
            render_results(results)

        return

    # ---- collection page ----
    if active is None:
        _ = st.info("Pick a collection from the sidebar.")
        return

    # Collections view (main panel)
    _ = st.subheader(f"{active.name} ({len(active.paper_ids)})")

    if not active.paper_ids:
        _ = st.caption("This collection is empty.")
        return

    # Build list of papers in the active collection (preserve order)
    collection_papers: list[Paper] = []
    for pid in active.paper_ids:
        p = by_id.get(pid)
        if p is not None:
            collection_papers.append(p)

    # If no paper selected yet, show the list and let user pick one.
    # If a paper is selected, show details (paper view) + keep list above.
    for p in collection_papers:
        label = p.title or "Untitled"
        if st.button(label, key=f"open_{p.paper_id}"):
            st.session_state["selected_paper_id"] = p.paper_id
            st.rerun()

    _ = st.divider()

    # Paper view (main panel)
    if selected_id is None:
        _ = st.caption("Select a paper above to view details.")
        return

    selected = by_id.get(selected_id)
    if selected is None:
        _ = st.warning("Selected paper not found.")
        return

    render_paper_view(selected)


if __name__ == "__main__":
    main()
