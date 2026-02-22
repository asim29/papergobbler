# PaperGobbler

A Streamlit app for searching and organizing research papers into collections,
powered by the [Semantic Scholar API](https://www.semanticscholar.org/product/api).

## Features

- **Search** — keyword search across millions of papers via Semantic Scholar
- **Browse** — view references, citations, and similar papers for any result
- **Detail view** — full metadata, TL;DR, DOI, citation/reference counts
- **Collections** — create named collections, add papers with one click
- **Collection management** — sort by year/citations/title, remove papers,
  view stats (year range, top venues)
- **Suggestions** — discover papers frequently cited by your collection
  (configurable overlap threshold)
- **Export / Import** — download a collection as JSON or import one back

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you haven't already.
2. Clone the repo and install dependencies:

   ```bash
   uv sync
   ```

3. Create a `.env` file with your Semantic Scholar API key:

   ```bash
   S2_API_KEY=your_key_here
   ```

   A key is optional but increases rate limits significantly.
   Get one at <https://www.semanticscholar.org/product/api>.

## Usage

```bash
uv run streamlit run app.py
```

Open the URL printed by Streamlit (usually <http://localhost:8501>).

## Development

```bash
# Lint, format, and type-check
uv run pre-commit run --all-files
```

All code must pass ruff, basedpyright, and markdownlint before committing.
