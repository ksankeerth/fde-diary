"""Does the embedding model read every chunk in full? Tokens per chunk, and how many answer rows the model sees."""
import numpy as np

from lab import CHUNKERS, DATA, DOCS
from questions import questions
from retrieval import outcomes
from run_benchmark import RESULTS
from search import MODEL, MODEL_KEY

CONTENT = MODEL.max_seq_length - 2  # tokens of text the model reads; [CLS] and [SEP] take the other two
SHOWN = ["fixed_size", "recursive", "layout_md_tables", "layout_stitched"]


def ntok(text):
    return len(MODEL.tokenizer(text, add_special_tokens=False)["input_ids"])


def row_end(chunk, row):
    """Index just after the row's cells (found in order, close together), or None if the row is not in the chunk."""
    start = 0
    while (i := chunk.find(row[0], start)) != -1:
        pos = i + len(row[0])
        for cell in row[1:]:
            j = chunk.find(cell, pos, pos + 250)
            if j == -1:
                break
            pos = j + len(cell)
        else:
            return pos
        start = i + 1
    return None


def rows_seen(chunks, qs, outs):
    """Row questions split by where the answer row sits: inside what the model reads, past its limit, or cut across chunks."""
    groups = {"seen": [], "past the limit": [], "cut across chunks": []}
    for q, (at3, at1, _) in zip(qs, outs):
        if "row" not in q:
            continue
        ends = [ntok(c[:e]) for c in chunks if (e := row_end(c, q["row"])) is not None]
        where = "cut across chunks" if not ends else "seen" if min(ends) <= CONTENT else "past the limit"
        groups[where].append((at3, at1))
    return groups


def share(hits, k):
    return f"{100 * sum(h[k] for h in hits) / len(hits):.1f}" if hits else "-"


def same_vector_check():
    """Embed the longest chunk, and again without its last 3 lines."""
    long = max(CHUNKERS["fixed_size"](DATA / "trailhead_regional_sales.pdf"), key=ntok)
    shorter = "\n".join(long.splitlines()[:-3])
    a, b = MODEL.encode([long, shorter], normalize_embeddings=True)
    return (f"Longest fixed_size chunk of the sales report ({ntok(long)} tokens) vs the same chunk without its last "
            f"3 lines ({ntok(shorter)} tokens): cosine similarity {float(a @ b):.6f}, "
            f"same vector: {'yes' if np.allclose(a, b, atol=1e-6) else 'no'}.")


if __name__ == "__main__":
    out = [f"Model: {MODEL_KEY}. It reads {CONTENT} tokens of text per chunk (max_seq_length {MODEL.max_seq_length}, "
           "counting [CLS] and [SEP]) and drops the rest.", ""]
    for doc in DOCS:
        qs = questions(doc)
        out += [f"### {doc}", "",
                "| chunker | chunks | median tokens | max tokens | chunks over limit | answer row seen (n, @3 / @1 %) | answer row past the limit (n, @3 / @1 %) | row cut across chunks (n) |",
                "|---|---|---|---|---|---|---|---|"]
        for cname in SHOWN:
            chunks = CHUNKERS[cname](DATA / doc)
            sizes = [ntok(c) for c in chunks]
            g = rows_seen(chunks, qs, outcomes(doc, CHUNKERS[cname], qs))
            cell = lambda hits: f"{len(hits)}, {share(hits, 0)} / {share(hits, 1)}"  # noqa: E731
            out.append(f"| {cname} | {len(chunks)} | {int(np.median(sizes))} | {max(sizes)} | {sum(s > CONTENT for s in sizes)} "
                       f"| {cell(g['seen'])} | {cell(g['past the limit'])} | {len(g['cut across chunks'])} |")
        out.append("")
    out += [same_vector_check(), ""]
    md = "\n".join(out)
    (RESULTS / f"tokens{'' if MODEL_KEY == 'minilm' else '-' + MODEL_KEY}.md").write_text(md)
    print(md)
