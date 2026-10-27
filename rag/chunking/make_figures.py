"""Figures for the layout-aware chunking write-up, drawn with Pillow from the real documents, chunks and results/*.json.

Run: uv run python make_figures.py   ->  figures/ (PNG, 1600 px wide)
"""
import json
import re
import textwrap
from functools import lru_cache
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

from lab import CHUNKERS, DATA, DOCS, fixed_size

HERE = Path(__file__).parent
RESULTS = HERE / "results"
OUT = HERE / "figures"
PLANS, SALES = "northwind_service_plans.docx", "trailhead_regional_sales.pdf"

W = 1600
PAD = 30
INK, MUTED, LINE, WHITE = "#0F172A", "#475569", "#CBD5E1", "#FFFFFF"
GREY, GREY_LIGHT, TEAL, TEAL_DARK = "#94A3B8", "#CBD5E1", "#0F766E", "#115E59"
GOOD, BAD = "#15803D", "#B91C1C"
CARD_GREY_BG, CARD_TEAL_BG = "#F1F5F9", "#F0FDFA"
HL_TEAL, HL_ROW, HL_CUT = "#99F6E4", "#FDE68A", "#FECACA"  # caption/header, answer row, the cut sentence

LABELS = {
    "fixed_size": "Character limit (1,000 chars)",
    "recursive": "Recursive splitter",
    "layout_md_tables": "Layout-aware",
    "layout_stitched": "Layout-aware + stitching",
}
COLORS = {"fixed_size": GREY, "recursive": GREY_LIGHT, "layout_md_tables": TEAL, "layout_stitched": TEAL_DARK}


# ---------------------------------------------------------------- drawing helpers
@lru_cache(maxsize=None)
def font(kind, size):
    paths = {
        "sans": ("/System/Library/Fonts/Helvetica.ttc", 0),
        "bold": ("/System/Library/Fonts/Helvetica.ttc", 1),
        "mono": ("/System/Library/Fonts/Menlo.ttc", 0),
        "monobold": ("/System/Library/Fonts/Menlo.ttc", 1),
        "symbol": ("/Library/Fonts/Arial Unicode.ttf", 0),
    }
    path, index = paths[kind]
    return ImageFont.truetype(path, size, index=index)


class Fig:
    """A 1600 px wide white canvas; `save` crops it to the content."""

    def __init__(self, height=4000):
        self.img = Image.new("RGB", (W, height), WHITE)
        self.d = ImageDraw.Draw(self.img)

    def text(self, xy, s, kind="sans", size=22, fill=INK, anchor="la"):
        self.d.text(xy, s, font=font(kind, size), fill=fill, anchor=anchor)

    def width(self, s, kind="sans", size=22):
        return self.d.textlength(s, font=font(kind, size))

    def wrapped(self, x, y, s, maxw, kind="sans", size=22, fill=INK, leading=1.35):
        """Word-wrapped sans text; returns the y below the last line."""
        f, line = font(kind, size), ""
        for word in s.split():
            if line and self.width(line + " " + word, kind, size) > maxw:
                self.text((x, y), line, kind, size, fill)
                y, line = y + int(size * leading), word
            else:
                line = (line + " " + word).strip()
        self.text((x, y), line, kind, size, fill)
        return y + int(size * leading)

    def mark(self, x, y, ok, size=26):
        """Green tick or red cross; (x, y) is the top left of the line the text next to it sits on."""
        self.text((x, y + 2), "✔" if ok else "✘", "symbol", size, GOOD if ok else BAD)

    def save(self, name, bottom):
        OUT.mkdir(parents=True, exist_ok=True)
        self.img.crop((0, 0, W, int(bottom) + PAD)).save(OUT / name)
        print("wrote", OUT / name)


def box(fig, x0, y0, x1, y1, fill, outline, radius=14, width=3):
    fig.d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill, outline=outline, width=width)


def dashed_line(fig, x0, x1, y, color, dash=18, gap=10, width=4):
    x = x0
    while x < x1:
        fig.d.line((x, y, min(x + dash, x1), y), fill=color, width=width)
        x += dash + gap


def squeeze(line):
    """Markdown tables pad cells with spaces and dashes; collapse that padding so a table row fits a card (display only)."""
    if line.startswith("|"):
        line = re.sub(r" {2,}", " ", line)
        line = re.sub(r"-{3,}", "---", line)
    return line


def layout_lines(lines, maxchars, indent="   ", max_rows=None):
    """Wrap each logical line to maxchars. Returns, per line, a list of (display text, start index in the source line)."""
    out = []
    for line in lines:
        line = line.replace("\r", "").replace("\x0c", "")  # PDF text carries \r and form feeds, which draw as boxes
        if len(line) <= maxchars:
            out.append([(line, 0)])
            continue
        rows, pos = [], 0
        for part in textwrap.wrap(line, maxchars - len(indent), drop_whitespace=False, break_on_hyphens=False, replace_whitespace=False) or [""]:
            rows.append((part if pos == 0 else indent + part, pos))
            pos += len(part)
        if max_rows and len(rows) > max_rows:
            rows = rows[:max_rows]
            rows[-1] = (rows[-1][0].rstrip()[: maxchars - 1] + "…", rows[-1][1])
        out.append(rows)
    return out


def draw_lines(fig, x, y, laid, size, highlights=None, line_h=None, indent_len=3):
    """Draws laid-out lines in monospace. highlights: {line index: colour} or {line index: (colour, start, end)}. Returns y below."""
    highlights = highlights or {}
    cw = font("mono", size).getlength("M")
    line_h = line_h or int(size * 1.45)
    for i, rows in enumerate(laid):
        hl = highlights.get(i)
        for row, start in rows:
            if hl:
                color, a, b = hl if isinstance(hl, tuple) else (hl, 0, 10**6)
                lead = indent_len if start else 0  # continuation rows are drawn with a hanging indent
                lo, hi = max(a - start, 0), min(b - start, len(row) - lead)
                if hi > lo:
                    fig.d.rectangle((x + (lo + lead) * cw - 3, y - 2, x + (hi + lead) * cw + 3, y + line_h - 4), fill=color)
            fig.text((x, y), row, "mono", size)
            y += line_h
    return y


# ---------------------------------------------------------------- figure 1
def fig1():
    pdf = pdfium.PdfDocument(str(DATA / SALES))
    pages = [pdf[i].render(scale=150 / 72).to_pil().convert("RGB") for i in range(2)]
    # crop boxes in the 150 dpi render: page 1 = heading, caption and the first rows; page 2 = top of the table
    crops = [pages[0].crop((165, 1165, 1100, 1500)), pages[1].crop((165, 135, 1100, 484))]
    cw = (W - 3 * PAD) // 2
    scale = cw / crops[0].width
    crops = [c.resize((cw, int(c.height * scale)), Image.LANCZOS) for c in crops]
    fig = Fig(1200)
    titles = ["Page 1: header row here", "Page 2: no header row"]
    colors = [GOOD, BAD]
    top = 90
    fig.text((PAD, 30), "The sales table runs over three pages, but its column names appear once", "bold", 30)
    for i, c in enumerate(crops):
        x = PAD + i * (cw + PAD)
        fig.text((x, top), titles[i], "bold", 26, colors[i])
        y = top + 46
        fig.img.paste(c, (x, y))
        fig.d.rectangle((x, y, x + cw, y + c.height), outline=LINE, width=2)
    y = top + 46
    # page 1: box round the header row (row at y 1258-1284 in the full render)
    hx0, hx1 = PAD, PAD + cw
    hy0, hy1 = y + int((1257 - 1165) * scale) - 3, y + int((1286 - 1165) * scale) + 3
    fig.d.rectangle((hx0 - 3, hy0, hx1 + 3, hy1), outline=GOOD, width=4)
    # page 2: dashed box round the first rows, which are data
    x2 = PAD + cw + PAD
    dy0, dy1 = y + int((149 - 135) * scale), y + int((226 - 135) * scale)
    for yy in (dy0, dy1):
        dashed_line(fig, x2 - 3, x2 + cw + 3, yy, BAD)
    for xx in (x2 - 3, x2 + cw + 3):
        fig.d.line((xx, dy0, xx, dy1), fill=BAD, width=4)
    bottom = y + crops[0].height + 24
    bottom = fig.wrapped(
        PAD, bottom, "Page 2 starts with 269, 332, 482, 467, 1,550. Which of those is Q1? Nothing on the page says.", W - 2 * PAD, size=26, fill=INK
    )
    fig.save("fig1-table-across-pages.png", bottom)


# ---------------------------------------------------------------- figure 2
def chunk_with_row(name, doc, needle=("Down Sleeping Bag", "Midwest")):
    return next(c for c in CHUNKERS[name](DATA / doc) if all(n in c for n in needle))


def card(fig, x, y, w, h, title, tcolor, bg, border, laid, hls, size, footer, fcolor, ok):
    box(fig, x, y, x + w, y + h, bg, border, width=4)
    ty = y + 18
    for line in textwrap.wrap(title, 56):
        fig.text((x + 22, ty), line, "bold", 26, tcolor)
        ty += 36
    draw_lines(fig, x + 22, ty + 14, laid, size, hls)
    fig.mark(x + 22, y + h - 56, ok, 28)
    fig.text((x + 62, y + h - 54), footer, "bold", 24, fcolor)


def fig2():
    left = chunk_with_row("fixed_size", SALES).split("\n")[:10]
    right = chunk_with_row("layout_stitched", SALES).split("\n")[:10]
    size, cw_card = 20, (W - 3 * PAD) // 2
    maxchars = int((cw_card - 44) // font("mono", size).getlength("M"))
    lay_l = layout_lines([squeeze(s) for s in left], maxchars)
    lay_r = layout_lines([squeeze(s) for s in right], maxchars, max_rows=3)
    row = lambda ls: next(i for i, s in enumerate(ls) if "Down Sleeping Bag" in s and "Midwest" in s)  # noqa: E731
    cap = next(i for i, s in enumerate(right) if s.startswith("Table 1:"))
    CAPTION = DOCS[SALES]["caption"]  # Docling's caption text also runs on into the closing paragraph; only the caption is highlighted
    hdr = next(i for i, s in enumerate(right) if s.startswith("| Product"))
    hls_r = {cap: (HL_TEAL, 0, len(CAPTION)), hdr: HL_TEAL, hdr + 1: HL_TEAL, row(right): HL_ROW}
    hls_l = {row(left): HL_ROW}
    lh = int(size * 1.45)
    n_rows = max(sum(len(r) for r in lay_l), sum(len(r) for r in lay_r))
    h = 18 + 36 * 1 + 14 + n_rows * lh + 90
    fig = Fig(h + 400)
    fig.text((PAD, 24), "The same rows of the sales table, as two chunking methods store them", "bold", 30)
    top = 90
    # the answer row is highlighted in both cards (amber); caption and header lines in teal
    card(fig, PAD, top, cw_card, h, "Character limit: a chunk from the middle of the table", MUTED, CARD_GREY_BG, GREY, lay_l, hls_l, size,
         "No column names, no caption", BAD, False)
    card(fig, 2 * PAD + cw_card, top, cw_card, h, "Layout-aware + stitching: the same rows", TEAL_DARK, CARD_TEAL_BG, TEAL, lay_r, hls_r, size,
         "Caption and column names travel with the rows", GOOD, True)
    ly = top + h + 22
    for x, color, label in [(PAD, HL_ROW, "row for Down Sleeping Bag, Midwest"), (PAD + 560, HL_TEAL, "caption and column names")]:
        fig.d.rectangle((x, ly + 4, x + 34, ly + 30), fill=color)
        fig.text((x + 46, ly), label, "sans", 24, MUTED)
    fig.save("fig2-chunk-cards.png", ly + 36)


# ---------------------------------------------------------------- figure 3
def fig3():
    chunks = fixed_size(DATA / PLANS)
    n = next(i for i, c in enumerate(chunks[:-1]) if c.endswith("Enterprise backups are"))
    end_lines = chunks[n].split("\n")[-3:]
    start_lines = chunks[n + 1].split("\n")[:2]
    size = 24
    maxchars = int((W - 2 * PAD - 80) // font("mono", size).getlength("M"))
    lay_a, lay_b = layout_lines(end_lines, maxchars), layout_lines(start_lines, maxchars)
    first_sentence_end = start_lines[0].index("Basic for 30 days.") + len("Basic for 30 days.")
    hl_a = {len(end_lines) - 1: (HL_CUT, 0, len(end_lines[-1]))}
    hl_b = {0: (HL_CUT, 0, first_sentence_end)}
    lh = int(size * 1.5)
    hh = 44 + sum(len(r) for r in lay_a) * lh + 24
    hb = 44 + sum(len(r) for r in lay_b) * lh + 24
    fig = Fig(1200)
    fig.text((PAD, 24), "A fixed-size cut lands in the middle of a sentence", "bold", 30)
    y = 90
    box(fig, PAD, y, W - PAD, y + hh, CARD_GREY_BG, GREY, width=3)
    fig.text((PAD + 24, y + 12), f"End of chunk {n + 1}", "bold", 22, MUTED)
    draw_lines(fig, PAD + 24, y + 48, lay_a, size, hl_a, line_h=lh)
    cut_y = y + hh + 38
    dashed_line(fig, PAD - 10, W - PAD + 10, cut_y, BAD, dash=26, gap=12, width=5)
    label = f"chunk {n + 1} ends here  /  chunk {n + 2} starts here"
    lw = fig.width(label, "bold", 24)
    fig.d.rectangle(((W - lw) / 2 - 16, cut_y - 20, (W + lw) / 2 + 16, cut_y + 20), fill=WHITE)
    fig.text((W / 2, cut_y), label, "bold", 24, BAD, anchor="mm")
    y2 = cut_y + 38
    box(fig, PAD, y2, W - PAD, y2 + hb, CARD_GREY_BG, GREY, width=3)
    fig.text((PAD + 24, y2 + 12), f"Start of chunk {n + 2}", "bold", 22, MUTED)
    draw_lines(fig, PAD + 24, y2 + 48, lay_b, size, hl_b, line_h=lh)
    bottom = fig.wrapped(PAD, y2 + hb + 24, "Asked how long Enterprise backups are kept, search can return the first fragment or the second, never the whole sentence.", W - 2 * PAD, size=26)
    fig.save("fig3-sentence-cut.png", bottom)


# ---------------------------------------------------------------- bar charts (figures 4 and 5)
def bar_groups(fig, y, groups, label_w=430, bar_h=34, gap=14, max_w=1000, title_size=26):
    """groups: [(group title, [(chunker key, value 0-100)])]. Horizontal bars with the chunker name on the left and the value at the end."""
    x0 = PAD + label_w
    for title, bars in groups:
        fig.text((PAD, y), title, "bold", title_size, INK)
        y += int(title_size * 1.5)
        for key, v in bars:
            fig.text((x0 - 14, y + bar_h / 2), LABELS[key], "sans", 22, INK, anchor="rm")
            if v > 0:
                fig.d.rectangle((x0, y, x0 + max_w * v / 100, y + bar_h), fill=COLORS[key])
            fig.text((x0 + max_w * v / 100 + 12, y + bar_h / 2), f"{v:g}%", "bold", 22, INK, anchor="lm")
            y += bar_h + gap
        y += 22
    return y


def fig4():
    rows = json.loads((RESULTS / "structure.json").read_text())
    docs = [(PLANS, "Service plans (Word document): the table fits on one page"), (SALES, "Regional sales (PDF): the table runs over three pages")]
    fig = Fig(2000)
    fig.text((PAD, 24), "Does a table chunk still carry the header row and the caption?", "bold", 30)
    y = 86
    for doc, doc_title in docs:
        by = {r["chunker"]: r for r in rows if r["doc"] == doc}
        fig.text((PAD, y), doc_title, "bold", 28, TEAL_DARK)
        y += 20
        y = bar_groups(fig, y + 28, [(t, [(k, by[k][m]) for k in LABELS]) for t, m in
                                      [("Table chunks with the header row", "header_pct"), ("Table chunks with the caption", "caption_pct")]])
        y += 14
        if doc == PLANS:
            fig.d.line((PAD, y - 12, W - PAD, y - 12), fill=LINE, width=2)
            y += 16
    fig.save("fig4-structure.png", y - 30)


def pooled(records, chunker, pattern_by_doc):
    """Correct@3 over the questions of several documents together, from each document's count of questions."""
    hit = n = 0
    for doc, pattern in pattern_by_doc.items():
        r = next(r for r in records if r["doc"] == doc and r["chunker"] == chunker and r["pattern"] == pattern)
        hit += round(r["correct_at_3"] * r["n"] / 100)
        n += r["n"]
    return round(100 * hit / n, 1), hit, n


def fig5():
    records = json.loads((RESULTS / "retrieval.json").read_text())
    at3 = lambda doc, pattern: {r["chunker"]: r["correct_at_3"] for r in records if r["doc"] == doc and r["pattern"] == pattern}  # noqa: E731
    patterns = [
        ("Plan feature (one-page table)", {k: v for k, v in at3(PLANS, "plan feature").items()}),
        ("Number lookup (table over 3 pages)", at3(SALES, "number lookup")),
        ("Text fact (both documents)", {k: pooled(records, k, {PLANS: "text fact", SALES: "text fact"})[0] for k in LABELS}),
    ]
    fig = Fig(2000)
    fig.text((PAD, 24), "Did search find the answer in its top 3 chunks?", "bold", 30)
    y = fig.wrapped(
        PAD, 70, "Share of questions where one of the top 3 chunks holds the answer and the column names needed to read it (n = 24 / 24 / 24)",
        W - 2 * PAD, size=24, fill=MUTED)
    y = bar_groups(fig, y + 20, [(t, [(k, d[k]) for k in LABELS]) for t, d in patterns])
    fig.save("fig5-retrieval.png", y - 10)
    return {t: {LABELS[k]: d[k] for k in LABELS} for t, d in patterns}


# ---------------------------------------------------------------- figure 6
def reason_text(pattern, reason, ok):
    if ok:
        return {"plan feature": "Answer row and column names", "number lookup": "Answer row and column names", "text fact": "Whole answer sentence", "what is this table": "Caption present"}[pattern]
    return {"no header row": "Row without column names", "row not in chunk": "Answer row is not in this chunk", "sentence cut": "Answer sentence is cut in two", "no caption": "No caption in this chunk"}.get(reason, reason)


def fig6():
    demo = json.loads((RESULTS / "demo.json").read_text())
    questions = list(dict.fromkeys((d["doc"], d["query"]) for d in demo))
    pattern = {SALES: "number lookup", PLANS: "plan feature"}
    qpat = {  # pattern of each demo question, to word the reason
        "How many Down Sleeping Bag units were sold in the Midwest region in Q1?": "number lookup",
        "Does the Basic plan include single sign-on?": "plan feature",
        "How long are backups kept on the Enterprise plan?": "text fact",
        "What does Table 1 show?": "what is this table",
    }
    qw, gap = 330, 20
    cwid = (W - 2 * PAD - qw - 2 * gap) // 2
    size = 20
    maxchars = int((cwid - 36) // font("mono", size).getlength("M"))
    xs = [PAD + qw + gap, PAD + qw + 2 * gap + cwid]
    lh = int(size * 1.45)
    fig = Fig(3000)
    fig.text((PAD, 24), "Top result for four questions", "bold", 30)
    y = 84
    for x, key, color in [(xs[0], "fixed_size", MUTED), (xs[1], "layout_stitched", TEAL_DARK)]:
        fig.text((x, y), LABELS[key], "bold", 24, color)
    fig.text((PAD, y), "Question", "bold", 24, MUTED)
    y += 46
    for doc, q in questions:
        entries = {d["chunker"]: d for d in demo if d["query"] == q}
        laid = {k: layout_lines([squeeze(s) for s in e["top1_first_lines"].split("\n")[:6]], maxchars, max_rows=1) for k, e in entries.items()}
        h = 18 + max(sum(len(r) for r in laid[k]) for k in laid) * lh + 18 + 52
        fig.d.line((PAD, y - 12, W - PAD, y - 12), fill=LINE, width=2)
        fig.wrapped(PAD, y + 8, q, qw, size=26)
        fig.text((PAD, y + h - 40), "Word document" if doc == PLANS else "PDF", "sans", 22, MUTED)
        for x, key in zip(xs, ["fixed_size", "layout_stitched"]):
            e = entries[key]
            teal = key == "layout_stitched"
            box(fig, x, y, x + cwid, y + h, CARD_TEAL_BG if teal else CARD_GREY_BG, TEAL if teal else GREY, radius=12, width=3)
            draw_lines(fig, x + 18, y + 16, laid[key], size, line_h=lh)
            fig.mark(x + 18, y + h - 50, e["correct"], 26)
            fig.text((x + 56, y + h - 48), reason_text(qpat[q], e["reason"], e["correct"]), "bold", 22, GOOD if e["correct"] else BAD)
        y += h + 36
    fig.save("fig6-search-demo.png", y - 30)


# ---------------------------------------------------------------- figure 0 (explainer)
CHUNK_COLORS = ["#0F766E", "#2563EB", "#D97706", "#7C3AED", "#DB2777", "#059669", "#DC2626"]  # colour-blind-friendly, one per chunk


def plans_pdf_chunks():
    """service-plans .docx -> PDF in a temp dir -> Docling -> the layout_stitched chunks. Returns (pdf page height, pdf bytes path, doc, chunks, texts)."""
    import subprocess
    import tempfile

    from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
    import lab
    from stitch import join_continuation_tables, link_captions

    tmp = Path(tempfile.mkdtemp(prefix="plans_pdf_"))
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(DATA / PLANS)],
                   check=True, capture_output=True)
    pdf_path = tmp / (Path(PLANS).stem + ".pdf")
    doc = lab.docling_doc(str(pdf_path)).model_copy(deep=True)
    link_captions(doc)
    join_continuation_tables(doc)
    chunker = HybridChunker(tokenizer=lab._tokenizer(), serializer_provider=lab._MarkdownTables())
    chunks = list(chunker.chunk(doc))
    texts = [lab._with_caption(chunker.contextualize(c), c, doc) for c in chunks]
    assert texts == lab.layout_stitched(pdf_path), "figure chunks differ from layout_stitched"
    return pdf_path, doc, chunks, texts


def chunk_regions(doc, chunks, texts, page_no, page_h):
    """{chunk index: (l, t, r, b)} in PDF points, top-left origin, for the part of each chunk that sits on page_no.
    Text chunks: union of the prov boxes of their doc_items (plus the heading when it is on the page). Table chunks all
    share one TableItem, so each gets the rows it holds, from the table cells' boxes (the first one also the caption)."""
    from docling_core.types.doc import TableItem

    def tl(p):  # BOTTOMLEFT (PDF points) -> top-left origin
        return (p.bbox.l, page_h - p.bbox.t, p.bbox.r, page_h - p.bbox.b)

    def union(boxes):
        return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))

    headings = {it.text: it for it, _ in doc.iterate_items() if str(it.label.value) == "section_header"}
    regions, cursor, seen_heading = {}, 1, set()
    for i, (c, text) in enumerate(zip(chunks, texts)):
        boxes = []
        table = next((it for it in c.meta.doc_items if isinstance(it, TableItem)), None)
        if table is None:
            for it in c.meta.doc_items:
                if str(it.label.value) != "caption":  # the caption is drawn with the first table chunk, where its text is embedded
                    boxes += [tl(p) for p in it.prov if p.page_no == page_no]
            h = headings.get((c.meta.headings or [None])[-1])
            if boxes and h is not None and h.self_ref not in seen_heading and any(p.page_no == page_no for p in h.prov):
                boxes += [tl(p) for p in h.prov if p.page_no == page_no]
            if boxes:
                seen_heading.add(h.self_ref if h is not None else None)
                regions[i] = union(boxes)
            continue
        # table chunk: rows of this chunk = the next len(body lines) rows after the header row
        lines = [ln for ln in text.split("\n") if ln.startswith("|")]
        body = lines[2:]
        cells = [t for t in table.data.table_cells if t.start_col_offset_idx == 0]
        first = {t.start_row_offset_idx: t for t in cells}
        rows = list(range(cursor, cursor + len(body)))
        for r, ln in zip(rows, body):
            assert ln.split("|")[1].strip() == first[r].text.strip(), (r, ln)
        first_chunk = cursor == 1
        cursor += len(body)
        # rows that are on this page: row tops run down the page, then jump back up on the next page
        page_rows, prev = [], -1
        for r in sorted(first):
            if first[r].bbox.t < prev:
                break
            page_rows.append(r)
            prev = first[r].bbox.t
        row_box = lambda r: (min(t.bbox.t for t in table.data.table_cells if t.start_row_offset_idx == r),  # noqa: E731
                             max(t.bbox.b for t in table.data.table_cells if t.start_row_offset_idx == r))
        mine = [r for r in ([0] if first_chunk else []) + rows if r in page_rows]
        if not mine:
            continue
        tp = next(p for p in table.prov if p.page_no == page_no)
        top = row_box(mine[0])[0]
        top = (top + row_box(mine[0] - 1)[1]) / 2 if mine[0] > 0 else top - 3
        bot = row_box(mine[-1])[1]
        bot = (bot + row_box(mine[-1] + 1)[0]) / 2 if mine[-1] + 1 in page_rows else page_h - tp.bbox.b + 1
        if first_chunk:  # the caption sits just above the table: it belongs to the first table chunk's area
            for ref in table.captions:
                cap = ref.resolve(doc)
                top = min(top, *(page_h - p.bbox.t - 2 for p in cap.prov if p.page_no == page_no))
        regions[i] = (tp.bbox.l, top, tp.bbox.r, bot)
    return regions


def fig_layout_explained():
    pdf_path, doc, chunks, texts = plans_pdf_chunks()
    pdf = pdfium.PdfDocument(str(pdf_path))
    page_no = next(i for i in range(len(pdf)) if "Table 3: Feature comparison by plan" in pdf[i].get_textpage().get_text_range()) + 1
    page_h = pdf[page_no - 1].get_size()[1]
    regions = chunk_regions(doc, chunks, texts, page_no, page_h)
    # only chunks that start on this page, so every card matches the text inside its box
    starts_here = [i for i in regions if next(p.page_no for p in chunks[i].meta.doc_items[0].prov) == page_no]
    order = sorted(starts_here, key=lambda i: (regions[i][1], i))[: len(CHUNK_COLORS)]
    color = {i: CHUNK_COLORS[n] for n, i in enumerate(order)}
    print(f"page {page_no}: chunks shown {order} of {len(chunks)}")

    # ---- left: the page, cropped sideways to the text block, with translucent regions and numbered badges
    left_w = int(W * 0.45) - PAD
    crop_x0, crop_x1, crop_y0, crop_y1 = 62, 566, 52, 742  # PDF points
    ppt = left_w / (crop_x1 - crop_x0)  # pixels per point on the figure
    render = pdf[page_no - 1].render(scale=120 / 72).to_pil().convert("RGBA")
    r2p = 120 / 72
    page = render.crop((int(crop_x0 * r2p), int(crop_y0 * r2p), int(crop_x1 * r2p), int(crop_y1 * r2p)))
    page = page.resize((left_w, int(page.height * left_w / page.width)), Image.LANCZOS)
    overlay = Image.new("RGBA", page.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    pad = 3
    rects = {}
    for n, i in enumerate(order):
        l, t, r, b = regions[i]
        rect = ((l - crop_x0) * ppt - pad, (t - crop_y0) * ppt - pad, (r - crop_x0) * ppt + pad, (b - crop_y0) * ppt + pad)
        rects[i] = rect
        rgb = tuple(int(color[i][k : k + 2], 16) for k in (1, 3, 5))
        od.rectangle(rect, fill=rgb + (64,), outline=rgb + (255,), width=3)
    page = Image.alpha_composite(page, overlay).convert("RGB")

    # ---- right: cards, one per chunk, same colour and number
    size, line_h, head_h = 22, 28, 34
    x_card = int(W * 0.45) + PAD // 2
    card_w = W - PAD - x_card
    maxchars = int((card_w - 40) // font("mono", size).getlength("M"))
    prepared = []
    for n, i in enumerate(order):
        lines = [ln.replace("\r", "") for ln in texts[i].split("\n") if ln.strip()]
        nh = len(chunks[i].meta.headings or [])
        content = [squeeze(ln) for ln in lines[nh:]]
        if len(content) > 4:  # table: caption, header row, separator, first data row ... more rows follow
            content = content[:4]
            if not content[-1].endswith("…"):
                content[-1] += " …"
            # one row per line, clipped (never wrapped) with a single ellipsis
            laid = [[(ln if len(ln) <= maxchars else ln[: maxchars - 1].rstrip(" …") + "…", 0)] for ln in content]
        else:
            laid = layout_lines(content, maxchars, indent="", max_rows=4)
        flat = [row for rows in laid for row in rows][:4]
        if sum(len(r) for r in laid) > 4:
            flat[-1] = (flat[-1][0].rstrip(" …")[: maxchars - 1] + "…", 0)
        prepared.append((" > ".join(lines[:nh]), flat))
    card_h = head_h + 4 * line_h + 26
    gap = 12
    cards_total = len(order) * card_h + (len(order) - 1) * gap
    top = 100
    body_h = max(page.height, cards_total)
    fig = Fig(top + body_h + 200)
    fig.text((PAD, 28), "Layout-aware chunking: the document's own structure decides the cuts", "bold", 30)
    py = top  # the top of the page image lines up with the top of the first card
    fig.img.paste(page, (PAD, py))
    fig.d.rectangle((PAD, py, PAD + left_w, py + page.height), outline=LINE, width=2)
    y = top
    for n, i in enumerate(order):
        c = color[i]
        bg = "#" + "".join(f"{int(int(c[k : k + 2], 16) * 0.08 + 255 * 0.92):02X}" for k in (1, 3, 5))
        box(fig, x_card, y, x_card + card_w, y + card_h, bg, c, radius=12, width=4)
        heading, rows = prepared[n]
        # badge on the card, same number as on the page
        fig.d.rounded_rectangle((x_card + 14, y + 10, x_card + 14 + 38, y + 10 + 38), radius=8, fill=c)
        fig.text((x_card + 33, y + 30), str(n + 1), "bold", 24, WHITE, anchor="mm")
        fig.text((x_card + 66, y + 14), heading, "bold", 24, MUTED)
        first_page = next(p.page_no for p in chunks[i].meta.doc_items[0].prov)
        if first_page != page_no:
            tag = f"starts on page {first_page}"
            fig.text((x_card + card_w - 18, y + 17), tag, "sans", 22, MUTED, anchor="ra")
        ry = y + head_h + 18
        for row, _ in rows:
            fig.text((x_card + 20, ry), row, "mono", size)
            ry += line_h
        # badge on the page, top-left of the region, in the left margin of the text block
        x0, y0 = PAD + rects[i][0], py + rects[i][1]
        fig.d.rounded_rectangle((x0 - 44, y0, x0 - 6, y0 + 38), radius=8, fill=c, outline=WHITE, width=2)
        fig.text((x0 - 25, y0 + 20), str(n + 1), "bold", 24, WHITE, anchor="mm")
        y += card_h + gap
    bottom = top + body_h + 18
    fig.text((PAD, bottom), "Each colour is one chunk. Headings travel with every chunk; table chunks repeat the caption and header row.", "sans", 24, MUTED)
    fig.save("fig0-layout-aware-explained.png", bottom + 30)


if __name__ == "__main__":
    for f in (fig_layout_explained, fig1, fig2, fig3, fig4, fig6):
        f()
    numbers = fig5()
    structure = json.loads((RESULTS / "structure.json").read_text())
    print(json.dumps({"fig5_correct_at_3": numbers}, indent=1))
    for r in structure:
        print(r["doc"], r["chunker"], "header", r["header_pct"], "caption", r["caption_pct"])
