Cells: correct@3 / correct@1, in % of questions, on the same chunks.

### one-page table: plan feature (n=24)

| chunker | minilm | bge-small |
|---|---|---|
| fixed_size | 50.0 / 25.0 | 45.8 / 16.7 |
| recursive | 8.3 / 4.2 | 8.3 / 0.0 |
| layout_default | 87.5 / 58.3 | 75.0 / 37.5 |
| layout_md_tables | 91.7 / 41.7 | 83.3 / 16.7 |
| layout_stitched | 83.3 / 25.0 | 66.7 / 8.3 |

### three-page table: number lookup (n=24)

| chunker | minilm | bge-small |
|---|---|---|
| fixed_size | 25.0 / 4.2 | 33.3 / 16.7 |
| recursive | 20.8 / 8.3 | 20.8 / 0.0 |
| layout_default | 29.2 / 25.0 | 29.2 / 20.8 |
| layout_md_tables | 33.3 / 29.2 | 33.3 / 16.7 |
| layout_stitched | 95.8 / 50.0 | 83.3 / 0.0 |

### plain text: text fact (n=24)

| chunker | minilm | bge-small |
|---|---|---|
| fixed_size | 83.3 / 45.8 | 83.3 / 50.0 |
| recursive | 100.0 / 79.2 | 95.8 / 75.0 |
| layout_default | 91.7 / 54.2 | 91.7 / 70.8 |
| layout_md_tables | 87.5 / 58.3 | 95.8 / 75.0 |
| layout_stitched | 79.2 / 45.8 | 83.3 / 75.0 |
