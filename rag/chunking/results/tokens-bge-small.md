Model: bge-small. It reads 510 tokens of text per chunk (max_seq_length 512, counting [CLS] and [SEP]) and drops the rest.

### northwind_service_plans.docx

| chunker | chunks | median tokens | max tokens | chunks over limit | answer row seen (n, @3 / @1 %) | answer row past the limit (n, @3 / @1 %) | row cut across chunks (n) |
|---|---|---|---|---|---|---|---|
| fixed_size | 11 | 208 | 257 | 0 | 23, 47.8 / 17.4 | 0, - / - | 1 |
| recursive | 13 | 186 | 267 | 0 | 24, 8.3 / 0.0 | 0, - / - | 0 |
| layout_md_tables | 19 | 164 | 253 | 0 | 24, 83.3 / 16.7 | 0, - / - | 0 |
| layout_stitched | 19 | 164 | 259 | 0 | 24, 66.7 / 8.3 | 0, - / - | 0 |

### trailhead_regional_sales.pdf

| chunker | chunks | median tokens | max tokens | chunks over limit | answer row seen (n, @3 / @1 %) | answer row past the limit (n, @3 / @1 %) | row cut across chunks (n) |
|---|---|---|---|---|---|---|---|
| fixed_size | 7 | 238 | 282 | 0 | 24, 33.3 / 16.7 | 0, - / - | 0 |
| recursive | 8 | 236 | 274 | 0 | 24, 20.8 / 0.0 | 0, - / - | 0 |
| layout_md_tables | 19 | 239 | 254 | 0 | 24, 33.3 / 16.7 | 0, - / - | 0 |
| layout_stitched | 47 | 245 | 254 | 0 | 24, 83.3 / 0.0 | 0, - / - | 0 |

Longest fixed_size chunk of the sales report (282 tokens) vs the same chunk without its last 3 lines (255 tokens): cosine similarity 0.998875, same vector: no.
