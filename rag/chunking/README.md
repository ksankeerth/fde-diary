# Chunking: does the way you cut a document change what search finds?

I cut the same two documents four different ways, put the chunks in a local vector database ([sqlite-vec](https://github.com/asg017/sqlite-vec) with the all-MiniLM-L6-v2 model) and asked 80 questions a person would type.

| Share of questions answered | One-page table | Three-page table | Plain text |
|---|---|---|---|
| Character limit (every 1,000 characters) | 50% | 25% | 83% |
| Recursive splitter | 8% | 21% | 100% |
| Layout-aware (Docling's HybridChunker) | 96% | 33% | 92% |
| Layout-aware + stitching | 83% | 92% | 75% |

A question counts as answered when one of the top 3 chunks holds the answer **and** the column names needed to read it (24 questions per column). Every question and its outcome: [results/per_question.md](results/per_question.md).

## The two documents

Written for this test, so they are free to share (`data/`):

- `northwind_service_plans.docx`: a service-plans document with a 40-row table on one page.
- `trailhead_regional_sales.pdf`: a sales report with a 90-row table over three pages, with the header row on page 1 only.

## What is in here

| File | What it does |
|---|---|
| `lab.py` | the four chunkers |
| `stitch.py` | joins a table that runs over several pages into one table, and links captions to their tables |
| `make_docs.py`, `questions.py` | the two documents, their ground truth and the 80 questions |
| `search.py` | vector search over chunks with sqlite-vec |
| `run_benchmark.py` | structure: header rows, captions, rows and sentences per chunker (`results/structure.md`) |
| `retrieval.py` | the 80 questions per chunker (`results/retrieval.md`, `results/per_question.md`) |
| `retrieval_demo.py` | four questions, side by side |
| `make_figures.py` | the figures in `figures/` |

## Run it

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/). The first run downloads Docling's models and the embedding model.

```bash
uv sync
uv run python run_benchmark.py    # structure of the chunks
uv run python retrieval.py        # retrieval: 80 questions
uv run python retrieval_demo.py   # four questions, side by side
```

The generated documents are already in `data/`. To rebuild them (`make_docs.py`) or the figures (`make_figures.py`) you also need [LibreOffice](https://www.libreoffice.org) on your `PATH` (`soffice`), and `make_figures.py` uses macOS fonts.
