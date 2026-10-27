"""Plain-language questions per document, each with what a single chunk must contain to answer it."""
import random
from collections import defaultdict

import pypdfium2 as pdfium

from lab import DATA, DOCS
from run_benchmark import norm, row_intact

N_ROW_GROUP, N_FACT, N_TABLE = 8, 12, 4  # 8 per plan (plans) or per page (sales); 24 row questions per document
EXTRA_TABLE_QUESTIONS = {"northwind_service_plans.docx": ["Which table lists the features of each plan?"]}  # truth.json has 3, 4 are needed


def row_group(doc, q):
    """What the row questions are balanced over: the plan named in the question, or the PDF page the row sits on."""
    spec = DOCS[doc]
    if doc.endswith(".pdf"):
        pdf = pdfium.PdfDocument(str(DATA / doc))
        row = spec["rows"][q["row"]]
        return next(i + 1 for i, page in enumerate(pdf) if row_intact([norm(page.get_textpage().get_text_range())], row, spec["rows"]))
    return next(h for h in spec["header"][1:] if f"{h} plan" in q["question"])


def questions(doc):
    """24 row questions, 12 text facts, 4 table questions: {pattern, question, and either `row` + `labels` or `must`}."""
    spec, rng = DOCS[doc], random.Random(7)
    groups = defaultdict(list)
    for q in spec["row_questions"]:
        groups[row_group(doc, q)].append(q)
    qs = []
    for group in sorted(groups):
        for q in rng.sample(groups[group], min(N_ROW_GROUP, len(groups[group]))):  # the whole row, with the column labels that explain its cells
            qs.append({"pattern": spec["row_pattern"], "question": q["question"], "row": spec["rows"][q["row"]], "labels": spec["header"][1:], "group": group})
    for f in rng.sample(spec["facts"], min(N_FACT, len(spec["facts"]))):  # the whole answer sentence
        qs.append({"pattern": "text fact", "question": f["question"], "must": f["sentence"], "reason": "sentence cut"})
    for text in (spec["table_questions"] + EXTRA_TABLE_QUESTIONS.get(doc, []))[:N_TABLE]:  # the caption
        qs.append({"pattern": "what is this table", "question": text, "must": spec["caption"], "reason": "no caption"})
    return qs


if __name__ == "__main__":
    for doc in DOCS:
        print(f"\n{doc}")
        for q in questions(doc):
            print(f"  [{q['pattern']}{' ' + str(q['group']) if 'group' in q else ''}] {q['question']}")
