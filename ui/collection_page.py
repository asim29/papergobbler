"""Collection page: view papers, sort, remove, suggestions, export/import."""

from __future__ import annotations

import json
import uuid
from collections import Counter
from typing import cast

import streamlit as st

from entities import Collection
from src.api import get_references
from src.storage import save_collection


def _get_active_collection() -> Collection | None:
    """Return the active collection or None."""
    active_id: str | None = st.session_state.get("active_collection_id")
    if active_id is None:
        return None
    collections = cast("list[Collection]", st.session_state.get("collections", []))
    for c in collections:
        if c.id == active_id:
            return c
    return None


def _int_field(
    metadata: dict[str, dict[str, object]], pid: str, field: str, default: int
) -> int:
    val = metadata.get(pid, {}).get(field)
    return val if isinstance(val, int) else default


def _sort_paper_ids(
    paper_ids: list[str],
    sort_by: str,
    titles: dict[str, str],
    metadata: dict[str, dict[str, object]],
) -> list[str]:
    """Return paper_ids sorted according to the chosen criterion."""
    if sort_by == "Date added":
        return list(paper_ids)

    if sort_by == "Title (A-Z)":
        return sorted(paper_ids, key=lambda pid: titles.get(pid, "").lower())

    if sort_by == "Year (newest)":
        return sorted(
            paper_ids,
            key=lambda pid: _int_field(metadata, pid, "year", 0),
            reverse=True,
        )

    if sort_by == "Year (oldest)":
        return sorted(
            paper_ids,
            key=lambda pid: _int_field(metadata, pid, "year", 9999),
        )

    if sort_by == "Citation count":
        return sorted(
            paper_ids,
            key=lambda pid: _int_field(metadata, pid, "citation_count", 0),
            reverse=True,
        )

    return list(paper_ids)


def _render_stats(collection: Collection) -> None:
    """Render collection statistics."""
    count = len(collection.paper_ids)
    _ = st.write(f"**Papers:** {count}")

    years = [
        cast("int", m.get("year"))
        for m in collection.paper_metadata.values()
        if isinstance(m.get("year"), int)
    ]
    if years:
        _ = st.write(f"**Year range:** {min(years)}–{max(years)}")

    venues = [
        cast("str", m.get("venue"))
        for m in collection.paper_metadata.values()
        if isinstance(m.get("venue"), str) and m.get("venue")
    ]
    if venues:
        top_venues = Counter(venues).most_common(3)
        venue_str = ", ".join(f"{v} ({n})" for v, n in top_venues)
        _ = st.write(f"**Top venues:** {venue_str}")


def _render_paper_list(collection: Collection) -> None:
    """Render the sorted paper list with remove buttons."""
    sort_by = st.selectbox(
        "Sort by",
        [
            "Year (newest)",
            "Year (oldest)",
            "Title (A-Z)",
            "Citation count",
            "Date added",
        ],
    )
    sorted_ids = _sort_paper_ids(
        collection.paper_ids,
        sort_by,
        collection.paper_titles,
        collection.paper_metadata,
    )

    if not sorted_ids:
        _ = st.info("No papers in this collection yet.")
        return

    for pid in sorted_ids:
        title = collection.paper_titles.get(pid, pid)
        meta = collection.paper_metadata.get(pid, {})
        year = meta.get("year")
        citations = meta.get("citation_count", 0)
        venue = meta.get("venue")

        parts = []
        if isinstance(year, int):
            parts.append(str(year))
        if isinstance(venue, str) and venue:
            parts.append(venue)
        parts.append(f"{citations} citations")
        meta_str = " · ".join(parts)

        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(title, key=f"title_{pid}"):
                from ui.detail_view import DetailView

                from ui.helpers import push_view

                push_view(DetailView(paper_id=pid))
                st.session_state["page"] = "search"
                st.rerun()
            _ = st.caption(meta_str)
        with col2:
            if st.button("Remove", key=f"rm_{pid}"):
                collection.paper_ids.remove(pid)
                _ = collection.paper_titles.pop(pid, None)
                _ = collection.paper_metadata.pop(pid, None)
                save_collection(collection)
                st.rerun()

        _ = st.divider()


def _render_suggestions(collection: Collection) -> None:
    """Render the suggestions panel (requires >= 5 papers)."""
    if len(collection.paper_ids) < 5:
        return

    _ = st.subheader("Suggestions")
    threshold = st.slider(
        "Minimum overlap",
        min_value=30,
        max_value=100,
        value=50,
        step=5,
        format="%d%%",
    )
    threshold_frac = threshold / 100.0

    if st.button("Refresh suggestions"):
        ref_counts: Counter[str] = Counter()
        ref_titles: dict[str, str] = {}
        collection_set = set(collection.paper_ids)

        with st.spinner("Fetching references..."):
            for pid in collection.paper_ids:
                refs, _ = get_references(pid, limit=100)
                for ref in refs:
                    if ref.paper_id not in collection_set:
                        ref_counts[ref.paper_id] += 1
                        ref_titles[ref.paper_id] = ref.title

        st.session_state["suggestions"] = {
            "counts": dict(ref_counts),
            "titles": ref_titles,
            "total": len(collection.paper_ids),
        }

    suggestions_data = st.session_state.get("suggestions")
    if not isinstance(suggestions_data, dict):
        return

    counts = cast("dict[str, int]", suggestions_data.get("counts", {}))
    titles = cast("dict[str, str]", suggestions_data.get("titles", {}))
    total = cast("int", suggestions_data.get("total", 1))
    collection_set = set(collection.paper_ids)

    filtered = [
        (pid, cnt)
        for pid, cnt in counts.items()
        if cnt / total >= threshold_frac and pid not in collection_set
    ]
    filtered.sort(key=lambda x: x[1], reverse=True)

    if not filtered:
        _ = st.info("No suggestions meet the current threshold.")
        return

    for pid, cnt in filtered:
        title = titles.get(pid, pid)
        col1, col2 = st.columns([5, 1])
        with col1:
            _ = st.write(f"**{title}**")
            _ = st.caption(f"Referenced by {cnt}/{total} papers")
        with col2:
            if st.button("Add", key=f"sug_add_{pid}"):
                from src.api import get_paper

                paper = get_paper(pid)
                collection.paper_ids.append(paper.paper_id)
                collection.paper_titles[paper.paper_id] = paper.title
                collection.paper_metadata[paper.paper_id] = {
                    "year": paper.year,
                    "citation_count": paper.citation_count,
                    "venue": paper.venue,
                }
                save_collection(collection)
                st.rerun()


def _render_export_import() -> None:
    """Render export/import controls."""
    _ = st.subheader("Export / Import")

    collection = _get_active_collection()
    if collection is not None:
        _ = st.download_button(
            "Export collection",
            data=json.dumps(collection.to_dict(), indent=2),
            file_name=f"{collection.name}.json",
            mime="application/json",
        )

    uploaded = st.file_uploader("Import collection", type=["json"])
    if uploaded is not None:
        raw = cast("object", json.loads(uploaded.read().decode("utf-8")))
        if isinstance(raw, dict):
            data = cast("dict[str, object]", raw)
            imported = Collection.from_dict(data)
            imported.id = str(uuid.uuid4())
            save_collection(imported)
            collections = cast(
                "list[Collection]", st.session_state.get("collections", [])
            )
            collections.append(imported)
            st.session_state["active_collection_id"] = imported.id
            st.rerun()


def render_collection_page() -> None:
    """Render the full collection management page."""
    collection = _get_active_collection()
    if collection is None:
        _ = st.info("Select a collection from the sidebar.")
        return

    _ = st.header(collection.name)

    _render_stats(collection)
    _ = st.divider()
    _render_paper_list(collection)
    _render_suggestions(collection)
    _ = st.divider()
    _render_export_import()
