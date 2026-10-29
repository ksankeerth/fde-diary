Cell: @3 / @1. A ✘ shows the reason the top-1 chunk fails the rule.

### northwind_service_plans.docx

| # | pattern | question | fixed_size | layout_stitched |
|---|---|---|---|---|
| 1 | plan feature | How can I contact support on the Basic plan? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 2 | plan feature | Is cross-region replication included in the Basic plan? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 3 | plan feature | Can I see penetration test results on the Basic plan? | ✔ / ✔ | ✔ / ✔ |
| 4 | plan feature | How much egress bandwidth does the Basic plan include? | ✔ / ✔ | ✔ / ✔ |
| 5 | plan feature | Does the Basic plan include single sign-on? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 6 | plan feature | Can I use my own encryption keys on the Basic plan? | ✔ / ✘ (row not in chunk) | ✘ / ✘ (row not in chunk) |
| 7 | plan feature | What is the API rate limit on the Basic plan? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 8 | plan feature | How large can a database be on the Basic plan? | ✔ / ✘ (row not in chunk) | ✔ / ✔ |
| 9 | plan feature | What uptime does the Enterprise plan guarantee? | ✘ / ✘ (row not in chunk) | ✘ / ✘ (row not in chunk) |
| 10 | plan feature | Can I use my own encryption keys on the Enterprise plan? | ✔ / ✔ | ✔ / ✘ (row not in chunk) |
| 11 | plan feature | How many users does the Enterprise plan include? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 12 | plan feature | Does the Enterprise plan include single sign-on? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 13 | plan feature | How many custom domains can I add on the Enterprise plan? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 14 | plan feature | How large can a database be on the Enterprise plan? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 15 | plan feature | Can I see penetration test results on the Enterprise plan? | ✔ / ✔ | ✔ / ✘ (row not in chunk) |
| 16 | plan feature | What contract terms does the Enterprise plan offer? | ✔ / ✘ (row not in chunk) | ✔ / ✔ |
| 17 | plan feature | How much object storage is included in the Team plan? | ✔ / ✔ | ✘ / ✘ (row not in chunk) |
| 18 | plan feature | Is private networking available on the Team plan? | ✘ / ✘ (row not in chunk) | ✘ / ✘ (row not in chunk) |
| 19 | plan feature | What contract terms does the Team plan offer? | ✔ / ✔ | ✔ / ✘ (row not in chunk) |
| 20 | plan feature | Does the Team plan include single sign-on? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 21 | plan feature | How large can a database be on the Team plan? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 22 | plan feature | How many read replicas can I have on the Team plan? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 23 | plan feature | Can I use my own encryption keys on the Team plan? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 24 | plan feature | Does the Team plan support point-in-time restore? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 25 | text fact | What hours is support available on the Team plan? | ✔ / ✔ | ✔ / ✔ |
| 26 | text fact | How many regions can Team customers choose from for their data? | ✔ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 27 | text fact | How quickly does revoking a customer-managed key make the data unreadable? | ✔ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 28 | text fact | How long are backups kept on the Enterprise plan? | ✘ / ✘ (sentence cut) | ✔ / ✔ |
| 29 | text fact | How often does the technical account manager hold a review call? | ✔ / ✔ | ✔ / ✘ (sentence cut) |
| 30 | text fact | How much does extra storage cost? | ✔ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 31 | text fact | What discount does annual prepayment give on the Team plan? | ✔ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 32 | text fact | How often are Enterprise databases backed up? | ✔ / ✔ | ✔ / ✔ |
| 33 | text fact | How quickly are critical vulnerabilities fixed? | ✘ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 34 | text fact | What is the charge for paying an invoice late? | ✔ / ✔ | ✔ / ✔ |
| 35 | text fact | How much notice do I need to cancel a monthly contract? | ✔ / ✔ | ✔ / ✔ |
| 36 | text fact | How long does Northwind keep data after an account is closed? | ✔ / ✔ | ✔ / ✔ |
| 37 | what is this table | What does Table 3 compare? | ✔ / ✔ | ✔ / ✔ |
| 38 | what is this table | Which table shows how the plans differ? | ✔ / ✔ | ✔ / ✔ |
| 39 | what is this table | What is Table 3 about? | ✔ / ✘ (no caption) | ✔ / ✔ |
| 40 | what is this table | Which table lists the features of each plan? | ✔ / ✔ | ✔ / ✔ |

### trailhead_regional_sales.pdf

| # | pattern | question | fixed_size | layout_stitched |
|---|---|---|---|---|
| 1 | number lookup | How many Trail Shoes units were sold in the Southwest region in Q1? | ✔ / ✘ (row not in chunk) | ✘ / ✘ (row not in chunk) |
| 2 | number lookup | How many Rain Shell Jacket units were sold in the Southeast region in Q3? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 3 | number lookup | How many Trail Shoes units were sold in the Southeast region in Q1? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 4 | number lookup | How many Trail Shoes units were sold in the Mountain region in Q1? | ✔ / ✔ | ✔ / ✘ (row not in chunk) |
| 5 | number lookup | How many Rain Shell Jacket units were sold in the Southeast region in Q4? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 6 | number lookup | How many Trail Shoes units were sold in the Northeast region in Q2? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 7 | number lookup | How many Trail Shoes units were sold in the Northeast region in Q3? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 8 | number lookup | How many Trail Shoes units were sold in the Pacific region in Q2? | ✔ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 9 | number lookup | How many Down Sleeping Bag units were sold in the Midwest region in Q1? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 10 | number lookup | How many Hydration Pack units were sold in the Southeast region in Q2? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 11 | number lookup | How many Headlamp units were sold in the Mountain region in Q2? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 12 | number lookup | How many Rain Shell Jacket units were sold in the Southwest region in Q3? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 13 | number lookup | How many Camp Stove units were sold in the Pacific region in Q2? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 14 | number lookup | How many Two-Person Tent units were sold in the Mountain region in Q3? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 15 | number lookup | How many Rain Shell Jacket units were sold in the Pacific region in Q2? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 16 | number lookup | How many Down Sleeping Bag units were sold in the Southeast region in Q3? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 17 | number lookup | How many Climbing Harness units were sold in the Midwest region in Q4? | ✘ / ✘ (no header row) | ✔ / ✘ (row not in chunk) |
| 18 | number lookup | How many Climbing Harness units were sold in the Midwest region in Q2? | ✘ / ✘ (no header row) | ✔ / ✘ (row not in chunk) |
| 19 | number lookup | How many Daypack 28L units were sold in the Mountain region in Q1? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 20 | number lookup | How many Water Filter units were sold in the Midwest region in Q3? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 21 | number lookup | How many Daypack 28L units were sold in the Mountain region in Q4? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 22 | number lookup | How many Gaiters units were sold in the Northeast region in Q3? | ✘ / ✘ (row not in chunk) | ✔ / ✘ (row not in chunk) |
| 23 | number lookup | How many Climbing Harness units were sold in the Midwest region in Q3? | ✘ / ✘ (no header row) | ✔ / ✔ |
| 24 | number lookup | How many Daypack 28L units were sold in the Midwest region in Q4? | ✘ / ✘ (row not in chunk) | ✔ / ✔ |
| 25 | text fact | Which temporary store is included in the Mountain region figures? | ✔ / ✔ | ✔ / ✔ |
| 26 | text fact | Which product sold the most units in 2025? | ✔ / ✔ | ✘ / ✘ (sentence cut) |
| 27 | text fact | Which quarter had the most unit sales? | ✔ / ✘ (sentence cut) | ✘ / ✘ (sentence cut) |
| 28 | text fact | How are the totals checked? | ✔ / ✘ (sentence cut) | ✘ / ✘ (sentence cut) |
| 29 | text fact | How many units did Trailhead Outfitters sell in 2025? | ✔ / ✔ | ✔ / ✔ |
| 30 | text fact | When are online orders counted as sold? | ✔ / ✔ | ✔ / ✘ (sentence cut) |
| 31 | text fact | Which states does the Mountain region cover? | ✘ / ✘ (sentence cut) | ✔ / ✔ |
| 32 | text fact | When will the next regional report be published? | ✘ / ✘ (sentence cut) | ✔ / ✔ |
| 33 | text fact | Are returns deducted from the sales figures? | ✔ / ✘ (sentence cut) | ✘ / ✘ (sentence cut) |
| 34 | text fact | How many stores does the Pacific region operate? | ✔ / ✔ | ✔ / ✔ |
| 35 | text fact | When did the Camp Stove promotion run? | ✔ / ✘ (sentence cut) | ✔ / ✘ (sentence cut) |
| 36 | text fact | Which region was the strongest in 2025? | ✔ / ✘ (sentence cut) | ✘ / ✘ (sentence cut) |
| 37 | what is this table | What does Table 1 show? | ✘ / ✘ (no caption) | ✔ / ✔ |
| 38 | what is this table | Where can I find units sold by product and region? | ✔ / ✘ (no caption) | ✔ / ✔ |
| 39 | what is this table | Which table has quarterly unit sales? | ✔ / ✘ (no caption) | ✔ / ✔ |
| 40 | what is this table | What is Table 1 about? | ✘ / ✘ (no caption) | ✔ / ✔ |
