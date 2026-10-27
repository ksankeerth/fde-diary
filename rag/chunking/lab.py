"""Five ways to chunk the same documents: two character-limit baselines, three layout-aware (Docling)."""
import json
from functools import lru_cache
from pathlib import Path

from docling_core.transforms.chunker.hierarchical_chunker import ChunkingDocSerializer, ChunkingSerializerProvider
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer

from stitch import join_continuation_tables, link_captions

DATA = Path(__file__).parent / "data"

# ---- Ground truth: what the test documents contain (make_docs.py wrote them from it) ----
DOCS = json.loads((DATA / "truth.json").read_text())  # per document: header, rows, caption, heading, facts, questions


# ---- 1. What a text-only pipeline sees ----
def plain_text(path) -> str:
    path = Path(path)
    if path.suffix == ".docx":
        import docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        d = docx.Document(str(path))
        lines = []
        for el in d.element.body.iterchildren():  # paragraphs and tables, in document order
            if el.tag.endswith("}p"):
                lines.append(Paragraph(el, d).text)
            elif el.tag.endswith("}tbl"):
                lines += [" | ".join(c.text for c in row.cells) for row in Table(el, d).rows]
        return "\n".join(lines)
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(path))
    return "\n".join(page.get_textpage().get_text_range() for page in pdf)


# ---- 2. What a layout-aware pipeline sees ----
@lru_cache(maxsize=None)
def docling_doc(path):
    from docling.document_converter import DocumentConverter

    return DocumentConverter().convert(str(path)).document


# ---- 3. Chunkers: path -> list of the texts that would be embedded ----
def fixed_size(path):
    text = plain_text(path)
    return [text[i : i + 1000] for i in range(0, len(text), 1000)]


def recursive(path):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(plain_text(path))


@lru_cache(maxsize=None)
def _tokenizer():
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

    # 256 MiniLM tokens is roughly 1000 characters, the same budget as the baselines
    return HuggingFaceTokenizer.from_pretrained(model_name="sentence-transformers/all-MiniLM-L6-v2", max_tokens=256)


def _hybrid(path, doc=None, caption_in_every_chunk=False, **chunker_args):
    from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

    chunker = HybridChunker(tokenizer=_tokenizer(), **chunker_args)
    doc = doc or docling_doc(str(path))
    texts = [(chunker.contextualize(c), c) for c in chunker.chunk(doc)]  # headings + chunk text
    return [_with_caption(text, c, doc) if caption_in_every_chunk else text for text, c in texts]


def _with_caption(text, chunk, doc):
    """Puts the caption of a table in the chunk after the heading lines, like the repeated header row: Docling's
    serializer writes a linked caption only into the table's first chunk."""
    from docling_core.types.doc import TableItem

    captions = [i.caption_text(doc) for i in chunk.meta.doc_items if isinstance(i, TableItem)]
    caption = next((c for c in captions if c), "")
    if not caption or caption in text:
        return text
    lines = text.split("\n")
    at = len(chunk.meta.headings or [])
    return "\n".join(lines[:at] + [caption] + lines[at:])


def layout_default(path):
    return _hybrid(path)


class _MarkdownTables(ChunkingSerializerProvider):
    """Serialize tables as Markdown, so every table chunk starts with the header row."""

    def get_serializer(self, doc):
        return ChunkingDocSerializer(doc=doc, table_serializer=MarkdownTableSerializer())


def layout_md_tables(path):
    return _hybrid(path, serializer_provider=_MarkdownTables())


def layout_stitched(path):
    """layout_md_tables after stitching (stitch.py): tables split across pages are joined into one,
    and captions are linked to their tables and kept in every table chunk."""

    doc = docling_doc(str(path)).model_copy(deep=True)  # the cached document stays untouched
    link_captions(doc)
    join_continuation_tables(doc)
    return _hybrid(path, doc, caption_in_every_chunk=True, serializer_provider=_MarkdownTables())


CHUNKERS = {
    "fixed_size": fixed_size,
    "recursive": recursive,
    "layout_default": layout_default,
    "layout_md_tables": layout_md_tables,
    "layout_stitched": layout_stitched,
}


if __name__ == "__main__":
    for name in DOCS:
        for cname, chunker in CHUNKERS.items():
            chunks = chunker(DATA / name)
            print(f"\n=== {name} | {cname} | {len(chunks)} chunks ===")
            print(chunks[0][:300] if chunks else "(none)")
