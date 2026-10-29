"""MiniLM vs bge-small on the same chunks: correct@3 and correct@1 per chunker and question group."""
import json

from lab import CHUNKERS
from run_benchmark import RESULTS

GROUPS = {"plan feature": "one-page table: plan feature", "number lookup": "three-page table: number lookup", "text fact": "plain text: text fact"}


def pooled(records, cname, pattern):
    """(n, correct@3 %, correct@1 %) over every record of the chunker and pattern (text fact: both documents)."""
    rs = [r for r in records if r["chunker"] == cname and r["pattern"] == pattern]
    n = sum(r["n"] for r in rs)
    hits = lambda k: sum(round(r[k] * r["n"] / 100) for r in rs)  # back to question counts, so pooling does not compound rounding  # noqa: E731
    return n, *(round(100 * hits(k) / n, 1) for k in ("correct_at_3", "correct_at_1"))


if __name__ == "__main__":
    minilm = json.loads((RESULTS / "retrieval.json").read_text())
    bge = json.loads((RESULTS / "retrieval-bge-small.json").read_text())
    out = ["Cells: correct@3 / correct@1, in % of questions, on the same chunks.", ""]
    for pattern, title in GROUPS.items():
        n = pooled(minilm, "fixed_size", pattern)[0]
        out += [f"### {title} (n={n})", "", "| chunker | minilm | bge-small |", "|---|---|---|"]
        for cname in CHUNKERS:
            cells = [f"{m[1]} / {m[2]}" for m in (pooled(minilm, cname, pattern), pooled(bge, cname, pattern))]
            out.append(f"| {cname} | {cells[0]} | {cells[1]} |")
        out.append("")
    md = "\n".join(out)
    (RESULTS / "model_comparison.md").write_text(md)
    print(md)
