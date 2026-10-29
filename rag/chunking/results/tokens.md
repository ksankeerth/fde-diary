Model: minilm. It reads 254 tokens of text per chunk (max_seq_length 256, counting [CLS] and [SEP]) and drops the rest.

### northwind_service_plans.docx

| chunker | chunks | median tokens | max tokens | chunks over limit | answer row seen (n, @3 / @1 %) | answer row past the limit (n, @3 / @1 %) | row cut across chunks (n) |
|---|---|---|---|---|---|---|---|
| fixed_size | 11 | 208 | 257 | 1 | 23, 52.2 / 26.1 | 0, - / - | 1 |
| recursive | 13 | 186 | 267 | 1 | 24, 8.3 / 4.2 | 0, - / - | 0 |
| layout_md_tables | 19 | 164 | 253 | 0 | 24, 91.7 / 41.7 | 0, - / - | 0 |
| layout_stitched | 19 | 164 | 259 | 1 | 24, 83.3 / 25.0 | 0, - / - | 0 |

### trailhead_regional_sales.pdf

| chunker | chunks | median tokens | max tokens | chunks over limit | answer row seen (n, @3 / @1 %) | answer row past the limit (n, @3 / @1 %) | row cut across chunks (n) |
|---|---|---|---|---|---|---|---|
| fixed_size | 7 | 238 | 282 | 3 | 24, 25.0 / 4.2 | 0, - / - | 0 |
| recursive | 8 | 236 | 274 | 2 | 24, 20.8 / 8.3 | 0, - / - | 0 |
| layout_md_tables | 19 | 239 | 254 | 0 | 24, 33.3 / 29.2 | 0, - / - | 0 |
| layout_stitched | 47 | 245 | 254 | 0 | 24, 95.8 / 50.0 | 0, - / - | 0 |

Longest fixed_size chunk of the sales report (282 tokens) vs the same chunk without its last 3 lines (255 tokens): cosine similarity 1.000000, same vector: yes.
