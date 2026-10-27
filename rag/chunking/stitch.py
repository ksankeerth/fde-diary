"""Stitching: put back together what Docling reads apart.

Docling returns a table that runs over several pages as one table per page, and leaves a "Table 3: ..." caption as a
plain paragraph. Run these two functions on the parsed document before chunking:

- link_captions: attach a "Table N:" or "Figure N:" paragraph to the table or picture next to it
- join_continuation_tables: join a table that continues on the next page into one table

Known limit: a table without a caption, directly followed by the caption of the next table (placed above that table),
takes that caption.
"""

from __future__ import annotations

import re

from docling_core.types.doc import (
    ContentLayer,
    DocItem,
    DocItemLabel,
    DoclingDocument,
    NodeItem,
    PictureItem,
    TableCell,
    TableItem,
    TextItem,
)

TABLE_CAPTION = re.compile(r"^(Table|Tab\.)\s*\d+[.:]", re.IGNORECASE)
FIGURE_CAPTION = re.compile(r"^(Figure|Fig\.)\s*\d+[.:]", re.IGNORECASE)
NUMBER = re.compile(r"^[\d.,%$ /-]+$")


# --- captions ------------------------------------------------------------------------------------------------


def link_captions(document: DoclingDocument) -> int:
    """Links a caption-shaped text next to a table or picture; the one before wins over the one after."""
    flow = _body_items(document)
    taken = {ref.cref for obj in (*document.tables, *document.pictures) for ref in obj.captions}
    linked = 0
    for index, item in enumerate(flow):
        pattern = _caption_pattern(item)
        if pattern is None or item.captions:
            continue
        caption = _neighbour_caption(flow, index, pattern, taken)
        if caption is None:
            continue
        item.captions.append(caption.get_ref())
        caption.label = DocItemLabel.CAPTION
        taken.add(caption.self_ref)
        linked += 1
    return linked


def _body_items(document: DoclingDocument) -> list[NodeItem]:
    return [item for item, _ in document.iterate_items(included_content_layers={ContentLayer.BODY})]


def _caption_pattern(item: NodeItem) -> re.Pattern[str] | None:
    if isinstance(item, TableItem):
        return TABLE_CAPTION
    if isinstance(item, PictureItem):
        return FIGURE_CAPTION
    return None


def _neighbour_caption(flow: list[NodeItem], index: int, pattern: re.Pattern[str], taken: set[str]) -> NodeItem | None:
    before = flow[index - 1 : index] if index > 0 else []
    for neighbour in (*before, *flow[index + 1 : index + 2]):
        if _is_free_caption(neighbour, flow[index], pattern, taken):
            return neighbour
    return None


def _is_free_caption(candidate: NodeItem, owner: NodeItem, pattern: re.Pattern[str], taken: set[str]) -> bool:
    return (
        isinstance(candidate, TextItem)
        and candidate.label in {DocItemLabel.TEXT, DocItemLabel.CAPTION}
        and candidate.parent == owner.parent
        and candidate.self_ref not in taken
        and pattern.match(candidate.text.strip()) is not None
    )


# --- tables split across pages -------------------------------------------------------------------------------


def join_continuation_tables(document: DoclingDocument) -> int:
    """Joins a table to the one that continues it on the next page, however many pages that takes."""
    joined = 0
    pair = _next_continuation(document)
    while pair is not None:
        _join(document, *pair)
        joined += 1
        pair = _next_continuation(document)
    return joined


def _next_continuation(document: DoclingDocument) -> tuple[TableItem, TableItem] | None:
    """Reading order is rebuilt after every join: deleting an item renumbers the items behind it."""
    flow = _flow_without_table_captions(document)
    for first, second in zip(flow, flow[1:], strict=False):
        if isinstance(first, TableItem) and isinstance(second, TableItem) and _continues(document, first, second):
            return first, second
    return None


def _flow_without_table_captions(document: DoclingDocument) -> list[NodeItem]:
    """A caption sits between its table and the one before; it is not content that separates two tables."""
    captions = {ref.cref for table in document.tables for ref in table.captions}
    return [item for item in _body_items(document) if item.self_ref not in captions]


def _continues(document: DoclingDocument, first: TableItem, second: TableItem) -> bool:
    return (
        _on_next_page(first, second)
        and first.data.num_cols == second.data.num_cols
        and _caption_allows_join(document, first, second)
        and _header_allows_join(first, second)
    )


def _on_next_page(first: TableItem, second: TableItem) -> bool:
    return bool(first.prov and second.prov) and first.prov[-1].page_no + 1 == second.prov[0].page_no


def _caption_allows_join(document: DoclingDocument, first: TableItem, second: TableItem) -> bool:
    caption = second.caption_text(document)
    return not caption or caption == first.caption_text(document)


def _header_allows_join(first: TableItem, second: TableItem) -> bool:
    """Header cells of their own that read differently make the second table a new table, unless they are data."""
    own_header = _texts(_flagged_cells(second))
    return not own_header or own_header == _texts(_header_cells(first)) or _flagged_row_is_data(first, second)


def _flagged_row_is_data(first: TableItem, second: TableItem) -> bool:
    """Docling flags the first data row of a continuation page as header; it reads like the body of the first table.

    Each cell has the kind of the first body row's cell (number or text), at least one column is a number, and no
    cell repeats the first table's header (that would be a repeated header, not data).
    """
    row = _texts(_flagged_row(second))
    header = _header_cells(first)
    body = _texts(_row_cells(first, max(cell.end_row_offset_idx for cell in header)))
    if not row or len(row) != len(body):
        return False
    kinds = [_is_number(text) for text in row]
    return (
        kinds == [_is_number(text) for text in body]
        and any(kinds)
        and all(text != head for text, head in zip(row, _texts(header), strict=False))
    )


def _flagged_row(table: TableItem) -> list[TableCell]:
    """The whole row of the first flagged cell: Docling leaves a cell of it unflagged now and then (a row span)."""
    flagged = _flagged_cells(table)
    return _row_cells(table, flagged[0].start_row_offset_idx) if flagged else []


def _is_number(text: str) -> bool:
    return NUMBER.match(text.strip()) is not None


def _flagged_cells(table: TableItem) -> list[TableCell]:
    return _in_reading_order([cell for cell in table.data.table_cells if cell.column_header])


def _row_cells(table: TableItem, row: int) -> list[TableCell]:
    return _in_reading_order([cell for cell in table.data.table_cells if cell.start_row_offset_idx == row])


def _header_cells(table: TableItem) -> list[TableCell]:
    """Docling often flags nothing; the first row is the header then."""
    return _flagged_cells(table) or _row_cells(table, 0)


def _in_reading_order(cells: list[TableCell]) -> list[TableCell]:
    return sorted(cells, key=lambda cell: (cell.start_row_offset_idx, cell.start_col_offset_idx))


def _texts(cells: list[TableCell]) -> list[str]:
    return [cell.text.strip() for cell in cells]


def _unflag_data_header(first: TableItem, second: TableItem) -> None:
    if _flagged_row_is_data(first, second):
        for cell in _flagged_row(second):
            cell.column_header = False


def _join(document: DoclingDocument, first: TableItem, second: TableItem) -> None:
    _unflag_data_header(first, second)
    repeats_header = _texts(_row_cells(second, 0)) == _texts(_header_cells(first))
    if repeats_header:
        for cell in _header_cells(first):
            cell.column_header = True
    skipped = 1 if repeats_header else 0
    shift = first.data.num_rows - skipped
    for cell in second.data.table_cells:
        if cell.start_row_offset_idx >= skipped:
            first.data.table_cells.append(_shifted(cell, shift))
    first.data.num_rows = shift + second.data.num_rows
    first.prov.extend(second.prov)
    first.footnotes.extend(second.footnotes)
    document.delete_items(node_items=[second, *_repeated_captions(document, first, second)])


def _shifted(cell: TableCell, rows: int) -> TableCell:
    return cell.model_copy(
        update={
            "start_row_offset_idx": cell.start_row_offset_idx + rows,
            "end_row_offset_idx": cell.end_row_offset_idx + rows,
        }
    )


def _repeated_captions(document: DoclingDocument, first: TableItem, second: TableItem) -> list[DocItem]:
    """The second table's caption goes with it only when it repeats the first table's."""
    if not second.captions or second.caption_text(document) != first.caption_text(document):
        return []
    return [ref.resolve(document) for ref in second.captions]
