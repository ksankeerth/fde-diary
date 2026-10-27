"""Structure metrics: does each chunker keep headers, captions, headings, rows and sentences intact?"""
import json
import re
from functools import lru_cache
from pathlib import Path

from lab import CHUNKERS, DATA, DOCS

RESULTS = Path(__file__).parent / "results"


def norm(text):
    return " ".join(text.split())  # collapse whitespace, keep case


def pct(part, whole):
    return round(100 * part / whole, 1) if whole else None


@lru_cache(maxsize=None)
def _row_starts(first_cells):
    return re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, sorted(set(first_cells), key=len, reverse=True))) + r")(?!\w)")


def row_intact(chunks, row, rows, fields=None):
    """Some chunk holds the row's first cell and, before a different first cell starts, the chosen other cells (default: all) in order.
    (Docling's default table format writes "Row, Column = value" pairs, so cells are matched in order, not as one line.)"""
    starts = _row_starts(tuple(r[0] for r in rows))
    for chunk in chunks:
        for m in starts.finditer(chunk):
            if m.group() != row[0]:
                continue
            nxt = next((n for n in starts.finditer(chunk, m.end()) if n.group() != row[0]), None)
            rest = chunk[m.end() : nxt.start() if nxt else len(chunk)]
            pos = 0
            for i in fields or range(1, len(row)):
                hit = re.compile(rf"(?<!\w){re.escape(row[i])}(?!\w)").search(rest, pos)
                if not hit:
                    break
                pos = hit.end()
            else:
                return True
    return False


def measure(doc, spec, cname, chunker):
    chunks = [norm(c) for c in chunker(DATA / doc)]
    rows = spec["rows"]
    rec = {"doc": doc, "chunker": cname, "chunks": len(chunks), "avg_chars": round(sum(map(len, chunks)) / len(chunks))}
    table = [c for c in chunks if any(row_intact([c], r, rows, (1, 2)) for r in rows)]  # chunks holding table rows
    rec["table_chunks"] = len(table)
    rec["header_pct"] = pct(sum(all(h in c for h in spec["header"][1:]) for c in table), len(table))  # column labels
    rec["caption_pct"] = pct(sum(spec["caption"] in c for c in table), len(table))
    rec["rows_intact_pct"] = pct(sum(row_intact(chunks, r, rows) for r in rows), len(rows))
    rec["heading_pct"] = pct(sum(spec["heading"] in c for c in table), len(table))
    # A chunk ends cleanly on sentence punctuation, a table-row bar, or a complete table row (which ends on its
    # last cell value). The last chunk ends the document, so it is never "cut".
    row_ends = tuple({r[-1] for r in rows})
    cut = sum(not (c[-1:] in tuple(".!?:|") or c.endswith(row_ends)) for c in chunks[:-1])
    rec["cut_sentences_pct"] = pct(cut, len(chunks))
    return rec


def to_markdown(records):
    cols = ["chunks", "avg_chars", "table_chunks", "header_pct", "caption_pct", "rows_intact_pct", "heading_pct", "cut_sentences_pct"]
    out = []
    for doc in DOCS:
        recs = [r for r in records if r["doc"] == doc]
        cols_doc = [c for c in cols if any(c in r for r in recs)]
        out += [f"### {doc}", "", "| chunker | " + " | ".join(cols_doc) + " |", "|---|" + "---|" * len(cols_doc)]
        out += [f"| {r['chunker']} | " + " | ".join(str(r.get(c, "")) for c in cols_doc) + " |" for r in recs]
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    records = [measure(doc, spec, cname, chunker) for doc, spec in DOCS.items() for cname, chunker in CHUNKERS.items()]
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "structure.json").write_text(json.dumps(records, indent=2))
    md = to_markdown(records)
    (RESULTS / "structure.md").write_text(md)
    print(md)
