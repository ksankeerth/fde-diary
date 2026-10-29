"""Retrieval test: does the top-3 for a question contain the answer together with its column labels?"""
import json

from lab import CHUNKERS, DATA, DOCS
from questions import questions
from run_benchmark import RESULTS, norm, pct, row_intact
from search import MODEL_KEY, build_index, search


def diagnose(chunk, q, rows):
    """'found' if the chunk answers the question, else the reason it does not."""
    chunk = norm(chunk)
    if "must" in q:
        return "found" if q["must"] in chunk else q["reason"]
    if not row_intact([chunk], q["row"], rows):
        return "row not in chunk"
    return "found" if all(label in chunk for label in q["labels"]) else "no header row"


def outcomes(doc, chunker, qs):
    """Per question: (correct@3, correct@1, reason of the top-1 chunk)."""
    db = build_index(chunker(DATA / doc))
    out = []
    for q in qs:
        reasons = [diagnose(text, q, DOCS[doc]["rows"]) for _, _, text in search(db, q["question"], 3)]
        out.append((any(r == "found" for r in reasons), reasons[0] == "found", reasons[0]))
    return out


def evaluate(doc, cname, qs, outs):
    hits = {}
    for q, (at3, at1, _) in zip(qs, outs):
        hits.setdefault(q["pattern"], []).append((at3, at1))
    return [
        {"doc": doc, "chunker": cname, "pattern": p, "n": len(h),
         "correct_at_3": pct(sum(a for a, _ in h), len(h)), "correct_at_1": pct(sum(b for _, b in h), len(h))}
        for p, h in hits.items()
    ]


COMPARE = ["fixed_size", "layout_stitched"]


def per_question(all_outs):
    """Every question with its outcome for fixed_size and layout_stitched, wins and losses alike.
    Cell: top-3 result / top-1 result; the reason is the one for the top-1 chunk."""
    mark = lambda ok: "✔" if ok else "✘"  # noqa: E731
    out = ["Cell: @3 / @1. A ✘ shows the reason the top-1 chunk fails the rule.", ""]
    for doc in DOCS:
        out += [f"### {doc}", "", "| # | pattern | question | " + " | ".join(COMPARE) + " |", "|---|---|---|" + "---|" * len(COMPARE)]
        for i, q in enumerate(questions(doc), 1):
            cells = []
            for cname in COMPARE:
                at3, at1, reason = all_outs[doc, cname][i - 1]
                cells.append(f"{mark(at3)} / {mark(at1)}" + ("" if at1 else f" ({reason})"))
            out.append(f"| {i} | {q['pattern']} | {q['question']} | " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


def to_markdown(records):
    out = ["Cells: correct@3 / correct@1, in % of questions.", ""]
    for doc in DOCS:
        recs = [r for r in records if r["doc"] == doc]
        patterns = list(dict.fromkeys(r["pattern"] for r in recs))
        n = {r["pattern"]: r["n"] for r in recs}
        out += [f"### {doc}", "", "| chunker | " + " | ".join(f"{p} (n={n[p]})" for p in patterns) + " |", "|---|" + "---|" * len(patterns)]
        for cname in CHUNKERS:
            by = {r["pattern"]: r for r in recs if r["chunker"] == cname}
            out.append(f"| {cname} | " + " | ".join(f"{by[p]['correct_at_3']} / {by[p]['correct_at_1']}" for p in patterns) + " |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    records, all_outs = [], {}
    for doc in DOCS:
        qs = questions(doc)
        for cname, chunker in CHUNKERS.items():
            all_outs[doc, cname] = outcomes(doc, chunker, qs)
            records += evaluate(doc, cname, qs, all_outs[doc, cname])
    suffix = "" if MODEL_KEY == "minilm" else f"-{MODEL_KEY}"  # minilm keeps the original file names
    (RESULTS / f"retrieval{suffix}.json").write_text(json.dumps(records, indent=2))
    md = to_markdown(records)
    (RESULTS / f"retrieval{suffix}.md").write_text(md)
    (RESULTS / f"per_question{suffix}.md").write_text(per_question(all_outs))
    print(md)
