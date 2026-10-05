# AI RAG Structure — <!-- TODO: Project Name -->

## Purpose

This document defines the rules, metadata schema, and workflow for the RAG (Retrieval-Augmented
Generation) knowledge pipeline that surfaces QuantConnect documentation to GitHub Copilot during
development of this algorithm.

The system has two layers:
1. **Static Skills Layer** (`docs/skills/`) — behavioral invariants derived from actual handler
   code. These never change unless the handler logic changes.
2. **Dynamic RAG Layer** (`rag/`) — QuantConnect API docs crawled, chunked, and indexed for
   BM25 keyword retrieval at query time.

---

## Source of Truth

- **QC Docs version:** v2 (`www.quantconnect.com/docs/v2/`)
- **Python API only** — all chunks tagged `language: python`
- **Platform:** `cloud` (QuantConnect hosted) unless explicitly tagged `lean-cli`
- Docs are public; no authentication required for crawling

---

## Metadata Schema

Every stored chunk carries this metadata:

```json
{
  "id": "<sha256 of url+header_path>",
  "source": "quantconnect-docs",
  "doc_version": "v2",
  "url": "https://www.quantconnect.com/docs/v2/writing-algorithms/...",
  "section_path": ["Writing Algorithms", "Section", "Subsection"],
  "language": "python",
  "platform": "cloud",
  "confidence": 1.0,
  "crawl_date": "YYYY-MM-DD"
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | SHA-256 of `url + header_path`; used for idempotent upserts |
| `source` | string | Always `"quantconnect-docs"` |
| `doc_version` | string | QC docs version tag (currently `"v2"`) |
| `url` | string | Canonical page URL |
| `section_path` | list[str] | Breadcrumb from root to nearest H2/H3 heading |
| `language` | string | `"python"` or `"csharp"` — Python chunks only ingested by default |
| `platform` | string | `"cloud"` or `"lean-cli"` |
| `confidence` | float | 1.0 for direct crawl; lower for inferred context |
| `crawl_date` | string | ISO date of most recent crawl |

---

## Chunking Rules

- Each chunk is one H2 or H3 section from the converted Markdown
- Target size: **200–500 tokens** per chunk
- Code blocks are **always kept with their surrounding explanation** — never split mid-block
- If a section exceeds 500 tokens after including its code block, the code block is preserved
  whole and the explanatory text is truncated at the nearest sentence boundary
- Chunks smaller than 50 tokens (e.g., stub headings) are merged with the next sibling

---

## Retrieval Rules

- Search method: **BM25 keyword scoring only** (`rank_bm25.BM25Okapi`)
- No embedding model, no vector DB, no GPU, no external services
- Default top-k: **5 chunks** per query
- Results ranked purely by BM25 score; no re-ranking
- Output written to `docs/RAG_CONTEXT.md` for Copilot consumption

---

## inject_context.py Workflow

```
Developer runs:
  python rag/inject_context.py --query "option chain filtering" --top-k 5

Pipeline:
  1. Load rag/data/doc_store.json  (all crawled chunks)
  2. Load rag/data/bm25_corpus.json  (pre-tokenized BM25 index)
  3. Score query against BM25 corpus
  4. Retrieve top-k chunk texts + metadata
  5. Write formatted Markdown to docs/RAG_CONTEXT.md

Copilot:
  - Reads docs/RAG_CONTEXT.md as workspace context
  - Uses chunks as authoritative QC API reference for that session
```

---

## Crawler Scope

Sections indexed by `rag/crawler/config.py` (`URL_SECTIONS`):

<!-- TODO: Update table as you enable sections in rag/crawler/config.py -->

| Section Key | QC Docs Path |
|---|---|
| `indicators` | `/writing-algorithms/indicators/` |
| `orders` | `/writing-algorithms/trading-and-orders/` |
| `data_subscriptions` | `/writing-algorithms/securities/asset-classes/` |
| `lifecycle` | `/writing-algorithms/initialization/` |
| `warmup` | `/writing-algorithms/historical-data/warm-up-periods/` |

To add a new section, see `rag/README.md` → **"Adding new QC doc URLs"**.

---

## Relationship to Skills Layer

Skills files (`docs/skills/`) describe *what the code does* — they are derived from handler
source and are not retrieved by BM25. They are always-available Copilot context via
`.github/copilot-instructions.md`.

The RAG layer describes *what the QC platform provides* — API signatures, platform behaviours,
edge cases documented in QC's official docs. Skills + RAG together give Copilot both the
strategy contract and the platform reference.

---

## Version Awareness

- If QC docs change in an incompatible way, re-run `ingest_pipeline.py` to refresh the corpus.
- The `crawl_date` field in each chunk's metadata allows staleness detection.
- Skills files must be updated manually when handler logic changes.
