"""Four questions, top-1 chunk for fixed_size vs layout_stitched, human-readable (and results/demo.json for the figures)."""
import json

from lab import CHUNKERS, DATA, DOCS
from questions import questions
from retrieval import diagnose
from run_benchmark import RESULTS
from search import build_index, search

COMPARE = ["fixed_size", "layout_stitched"]
PLANS, SALES = "northwind_service_plans.docx", "trailhead_regional_sales.pdf"
DEMO = [  # (document, question text), in the order shown in the post
    (SALES, "How many Down Sleeping Bag units were sold in the Midwest region in Q1?"),
    (PLANS, "Does the Basic plan include single sign-on?"),
    (PLANS, "How long are backups kept on the Enterprise plan?"),
    (SALES, "What does Table 1 show?"),
]


def find_question(doc, text):
    """The question dict (with what a chunk must contain) from questions.py; if it was not sampled there, build it from truth.json."""
    q = next((q for q in questions(doc) if q["question"] == text), None)
    if q:
        return q
    spec = DOCS[doc]
    if (r := next((r for r in spec["row_questions"] if r["question"] == text), None)):
        return {"pattern": spec["row_pattern"], "question": text, "row": spec["rows"][r["row"]], "labels": spec["header"][1:]}
    if (f := next((f for f in spec["facts"] if f["question"] == text), None)):
        return {"pattern": "text fact", "question": text, "must": f["sentence"], "reason": "sentence cut"}
    assert text in spec["table_questions"], text
    return {"pattern": "what is this table", "question": text, "must": spec["caption"], "reason": "no caption"}


if __name__ == "__main__":
    out = []
    for doc, text in DEMO:
        q = find_question(doc, text)
        print(f"\n{'=' * 78}\n[{doc}] {q['question']}")
        for cname in COMPARE:
            _, _, chunk = search(build_index(CHUNKERS[cname](DATA / doc)), q["question"], 1)[0]
            reason = diagnose(chunk, q, DOCS[doc]["rows"])
            top = "\n".join(chunk.splitlines()[:6])
            print(f"\n--- {cname}: top-1 chunk ---\n{top}\n{'✔' if reason == 'found' else '✘'} {reason}")
            out.append({"doc": doc, "query": q["question"], "chunker": cname, "top1_first_lines": top, "correct": reason == "found", "reason": reason})
    (RESULTS / "demo.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
