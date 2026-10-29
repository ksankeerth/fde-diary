# Chunking: does the way you cut a document change what search finds?

I cut the same two documents four different ways, put the chunks in a local vector database ([sqlite-vec](https://github.com/asg017/sqlite-vec) with the all-MiniLM-L6-v2 model) and asked 80 questions a person would type.

| Share of questions answered | One-page table | Three-page table | Plain text |
|---|---|---|---|
| Character limit (every 1,000 characters) | 50% | 25% | 83% |
| Recursive splitter | 8% | 21% | 100% |
| Layout-aware (Docling's HybridChunker) | 92% | 33% | 92% |
| Layout-aware + stitching | 83% | 96% | 79% |

A question counts as answered when one of the top 3 chunks holds the answer **and** the column names needed to read it (24 questions per column). Every question and its outcome: [results/per_question.md](results/per_question.md).

## Does the embedding model's input limit matter?

all-MiniLM-L6-v2 reads at most 256 tokens (254 of text plus two special tokens) and ignores the rest of a chunk. To see whether that hides answers, I ran the same chunks through `BAAI/bge-small-en-v1.5`, which reads up to 512 tokens and so takes every chunk in full (the longest has 282 tokens). Cells: correct@3 / correct@1, in % of questions.

| Chunker | One-page table (n=24) MiniLM | bge-small | Three-page table (n=24) MiniLM | bge-small | Plain text (n=24) MiniLM | bge-small |
|---|---|---|---|---|---|---|
| Character limit | 50.0 / 25.0 | 45.8 / 16.7 | 25.0 / 4.2 | 33.3 / 16.7 | 83.3 / 45.8 | 83.3 / 50.0 |
| Recursive splitter | 8.3 / 4.2 | 8.3 / 0.0 | 20.8 / 8.3 | 20.8 / 0.0 | 100.0 / 79.2 | 95.8 / 75.0 |
| Layout-aware, default tables | 87.5 / 58.3 | 75.0 / 37.5 | 29.2 / 25.0 | 29.2 / 20.8 | 91.7 / 54.2 | 91.7 / 70.8 |
| Layout-aware | 91.7 / 41.7 | 83.3 / 16.7 | 33.3 / 29.2 | 33.3 / 16.7 | 87.5 / 58.3 | 95.8 / 75.0 |
| Layout-aware + stitching | 83.3 / 25.0 | 66.7 / 8.3 | 95.8 / 50.0 | 83.3 / 0.0 | 79.2 / 45.8 | 83.3 / 75.0 |

With the limit set to 254 tokens the layout-aware chunks fit MiniLM almost exactly, and for no table question does the answer row lie past the point where MiniLM stops reading, so the limit does not explain the misses. The model that reads every chunk in full finds no more: its results are about the same or a little lower, so the gaps between the chunkers come from how the document is cut, not from what the model drops. Details: [results/model_comparison.md](results/model_comparison.md), [results/tokens.md](results/tokens.md).

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
| `search.py` | vector search over chunks with sqlite-vec (all-MiniLM-L6-v2, or bge-small with `EMBED_MODEL=bge-small`) |
| `run_benchmark.py` | structure: header rows, captions, rows and sentences per chunker (`results/structure.md`) |
| `retrieval.py` | the 80 questions per chunker (`results/retrieval.md`, `results/per_question.md`); `EMBED_MODEL=bge-small` runs it with the second model (`results/retrieval-bge-small.md`) |
| `token_check.py` | tokens per chunk, and whether the embedding model reads all of it (`results/tokens.md`, `results/tokens-bge-small.md`) |
| `compare_models.py` | the two models side by side (`results/model_comparison.md`) |
| `retrieval_demo.py` | four questions, side by side |
| `make_figures.py` | the figures in `figures/` |

## Run it

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/). The first run downloads Docling's models and the embedding model.

```bash
uv sync
uv run python run_benchmark.py    # structure of the chunks
uv run python retrieval.py        # retrieval: 80 questions
uv run python retrieval_demo.py   # four questions, side by side

# the same with a second embedding model, and the comparison
EMBED_MODEL=bge-small uv run python retrieval.py
uv run python token_check.py
EMBED_MODEL=bge-small uv run python token_check.py
uv run python compare_models.py
```

The generated documents are already in `data/`. To rebuild them (`make_docs.py`) or the figures (`make_figures.py`) you also need [LibreOffice](https://www.libreoffice.org) on your `PATH` (`soffice`), and `make_figures.py` uses macOS fonts.
