"""Write the two test documents and their ground truth (data/truth.json). All content is fictional and fixed."""
import json
import random
import subprocess
from datetime import datetime
from pathlib import Path

import docx
import pypdfium2 as pdfium
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------------------------
# Document 1: Northwind Cloud service plans (docx)
# ---------------------------------------------------------------------------------------------
PLANS_HEADER = ["Feature", "Basic", "Team", "Enterprise"]
PLANS_CAPTION = "Table 3: Feature comparison by plan"
PLANS_HEADING = "Comparing the plans"
PLANS_ROWS = [
    ["Included users", "5", "50", "Unlimited"],
    ["Projects", "3", "25", "Unlimited"],
    ["Price per user", "$12 / user / month", "$29 / user / month", "$58 / user / month"],
    ["Annual prepayment discount", "No", "10%", "15%"],
    ["Contract term", "Monthly", "Monthly or annual", "Annual or multi-year"],
    ["Block storage per user", "5 GB", "50 GB", "500 GB"],
    ["Object storage included", "100 GB", "2 TB", "50 TB"],
    ["Egress bandwidth included", "100 GB", "1 TB", "20 TB"],
    ["Managed databases", "2", "10", "40"],
    ["Maximum database size", "20 GB", "250 GB", "4 TB"],
    ["Read replicas", "No", "Up to 2", "Up to 10"],
    ["Autoscaling", "No", "Yes", "Yes"],
    ["Custom domains", "1", "10", "50"],
    ["Webhooks", "5", "50", "500"],
    ["API requests per minute", "600", "6,000", "60,000"],
    ["Monthly uptime commitment", "99.5%", "99.9%", "99.99%"],
    ["SLA service credits", "No", "10% of monthly fee", "25% of monthly fee"],
    ["Support channels", "Email only", "Email and chat", "Email, chat and phone"],
    ["First response, severity 1", "1 business day", "4 hours", "30 minutes"],
    ["Round-the-clock support", "No", "No", "Yes"],
    ["Technical account manager", "No", "No", "Yes"],
    ["Onboarding sessions", "No", "1 session", "4 sessions"],
    ["Backup retention", "30 days", "90 days", "365 days"],
    ["Backup frequency", "Once a day", "Every 12 hours", "Every 6 hours"],
    ["Deleted resource recovery", "7 days", "14 days", "30 days"],
    ["Point-in-time restore", "No", "Yes", "Yes"],
    ["Cross-region replication", "No", "Optional", "Yes"],
    ["Single sign-on (SAML)", "No", "Yes", "Yes"],
    ["Multi-factor authentication", "Yes", "Yes", "Yes"],
    ["Role-based access control", "Fixed roles", "Custom roles", "Custom roles with approvals"],
    ["Audit log retention", "30 days", "6 months", "12 months"],
    ["Customer-managed encryption keys", "No", "No", "Yes"],
    ["Private networking", "No", "Yes", "Yes"],
    ["IP allow list size", "10 entries", "100 entries", "1,000 entries"],
    ["Compliance reports", "Public trust page", "SOC 2 summary", "SOC 2 Type II and ISO 27001"],
    ["Penetration test summary", "No", "No", "Yes"],
    ["Data residency choice", "Closest region", "3 regions", "14 regions"],
    ["Team workspaces", "1", "10", "100"],
    ["Usage alerts", "Email", "Email and Slack", "Email, Slack and PagerDuty"],
    ["Invoice payment", "Card only", "Card or invoice", "Card, invoice or purchase order"],
]

# Feature questions: (row label, wording with {plan})
PLANS_FEATURE_QUESTIONS = [
    ("Single sign-on (SAML)", "Does the {plan} plan include single sign-on?"),
    ("Customer-managed encryption keys", "Can I use my own encryption keys on the {plan} plan?"),
    ("Private networking", "Is private networking available on the {plan} plan?"),
    ("Point-in-time restore", "Does the {plan} plan support point-in-time restore?"),
    ("Cross-region replication", "Is cross-region replication included in the {plan} plan?"),
    ("Technical account manager", "Do I get a technical account manager on the {plan} plan?"),
    ("Included users", "How many users does the {plan} plan include?"),
    ("Object storage included", "How much object storage is included in the {plan} plan?"),
    ("API requests per minute", "What is the API rate limit on the {plan} plan?"),
    ("Read replicas", "How many read replicas can I have on the {plan} plan?"),
    ("Support channels", "How can I contact support on the {plan} plan?"),
    ("Monthly uptime commitment", "What uptime does the {plan} plan guarantee?"),
    ("Penetration test summary", "Can I see penetration test results on the {plan} plan?"),
    ("Contract term", "What contract terms does the {plan} plan offer?"),
    ("Usage alerts", "Where are usage alerts sent on the {plan} plan?"),
    ("Maximum database size", "How large can a database be on the {plan} plan?"),
    ("Custom domains", "How many custom domains can I add on the {plan} plan?"),
    ("Egress bandwidth included", "How much egress bandwidth does the {plan} plan include?"),
]

# Each section: (heading level, heading, paragraphs); a paragraph is a list of sentences.
PLANS_SECTIONS = [
    (1, "Overview", [
        ["Northwind Cloud offers managed hosting, storage and databases to teams of every size.",
         "This document describes the three service plans that take effect on 1 January 2026: Basic, Team and Enterprise.",
         "It replaces the 2025 plan sheet, and the prices in it apply to every new subscription from that date."],
        ["Existing customers keep their current terms until their next renewal date.",
         "At renewal they are moved to the closest 2026 plan automatically, and the account owner receives written notice 45 days beforehand.",
         "Nobody is moved to a plan that costs more without a confirmation step."],
        ["All plans run in the same 14 regions and use the same infrastructure.",
         "The plans differ in included capacity, support response times, retention periods and security controls, not in the quality of the underlying service."],
    ]),
    (1, "Choosing a plan", []),
    (2, "Who each plan is for", [
        ["Basic is built for individuals, students and small side projects.",
         "It is limited to 5 users and 3 projects, and it includes enough storage for a typical static site, a small API or a hobby database.",
         "Basic accounts can be upgraded at any time, and the price difference is prorated to the day."],
        ["Team is the plan most customers choose.",
         "It supports up to 50 users and 25 projects, adds single sign-on, private networking and point-in-time restore, and moves support from email only to email and chat.",
         "Most teams of 10 to 40 engineers run comfortably within its included capacity."],
        ["Enterprise has no user or project limits.",
         "It adds customer-managed encryption keys, cross-region replication, a named technical account manager and round-the-clock support for severity 1 incidents.",
         "It is the only plan that offers a multi-year contract with a price lock for the full term."],
    ]),
    (2, "Moving between plans", [
        ["You can move to a higher plan whenever you like.",
         "Moving to a lower plan takes effect at the end of the current billing period, and resources above the lower plan's limits must be removed or archived before then.",
         "Northwind will not delete anything on your behalf during a downgrade."],
        ["A 30-day trial of the Team plan is available to every new account.",
         "No payment card is required for the trial, and any resources created during the trial are kept if you convert to a paid plan within 14 days of its end."],
    ]),
    (2, PLANS_HEADING, [
        ["The table below lists the limits and features that differ between the plans.",
         "Where a cell says Yes, the feature is included at no extra charge."],
    ]),
    "TABLE",
    (None, None, [
        ["Limits in the table apply per account unless stated otherwise.",
         "Add-ons such as extra storage and additional read replicas are priced in the Billing section."],
    ]),
    (1, "Support", []),
    (2, "Response times", [
        ["Support requests are classified into four severity levels.",
         "Severity 1 means a production system is down or data is at risk, and severity 4 is a general question.",
         "Target first-response times for severity 1 are 1 business day on Basic, 4 hours on Team and 30 minutes on Enterprise."],
        ["Enterprise customers can reach an engineer by phone at any hour, every day of the year.",
         "Team and Basic requests are handled between 06:00 and 20:00 UTC on weekdays, and requests that arrive outside those hours wait until the next working morning."],
    ]),
    (2, "Channels and account management", [
        ["Basic includes email support only.",
         "Team adds live chat from the Northwind console, and Enterprise adds a dedicated phone line and a shared Slack channel with our on-call engineers."],
        ["Each Enterprise account has a named technical account manager who holds a review call every quarter, covering usage, incidents and upcoming product changes.",
         "Team accounts receive one onboarding session in their first month, and Enterprise accounts receive four sessions spread over their first quarter."],
        ["The public status page at status.northwind.example lists incidents as they are confirmed and keeps a history of the last 24 months.",
         "Subscribers to the page receive updates by email or webhook."],
    ]),
    (1, "Data retention and backups", []),
    (2, "Backups", [
        ["Enterprise backups are kept for 365 days; Team backups for 90 days; Basic for 30 days.",
         "Backups are taken automatically and stored in a second region that is at least 400 kilometres from the primary one."],
        ["Basic databases are backed up once a day, Team databases every 12 hours and Enterprise databases every 6 hours.",
         "Team and Enterprise customers can also restore a database to any second within the retention window, using point-in-time restore."],
        ["Northwind restores a random sample of backups every week to confirm that they can be read.",
         "Failed restore tests open an internal incident, and customers affected by a failed test are notified within 24 hours."],
    ]),
    (2, "Deleted resources and closed accounts", [
        ["A deleted resource can be recovered for 7 days on Basic, 14 days on Team and 30 days on Enterprise.",
         "After that period the resource can only be rebuilt from a backup."],
        ["When an account is closed, Northwind keeps its data for 60 days so that the owner can export it.",
         "On day 61 the data is deleted from production systems, and a deletion certificate is sent to the account owner on request."],
        ["Audit logs are kept for 30 days on Basic, 6 months on Team and 12 months on Enterprise.",
         "Logs can be exported to your own storage at any time, and exported logs are not affected by these limits."],
    ]),
    (1, "Security", []),
    (2, "Encryption and access", [
        ["All data is encrypted with AES-256 at rest and with TLS 1.3 in transit.",
         "Enterprise customers can supply their own encryption keys, which they can revoke at any time; revoking a key makes the data unreadable within 15 minutes."],
        ["Multi-factor authentication is required for every administrator on every plan.",
         "Single sign-on through SAML 2.0 is available on Team and Enterprise, and sessions end after 8 hours of inactivity unless the account owner sets a shorter limit."],
        ["Private networking lets resources talk to each other without crossing the public internet, and it is available on Team and Enterprise.",
         "IP allow lists are limited to 10 entries on Basic, 100 on Team and 1,000 on Enterprise."],
    ]),
    (2, "Assurance", [
        ["Northwind is audited every year against SOC 2 Type II and ISO 27001.",
         "Enterprise customers receive the full SOC 2 Type II report and the ISO 27001 certificate under a non-disclosure agreement, Team customers receive a summary of the SOC 2 findings, and Basic customers can read the public trust page."],
        ["An independent firm performs a penetration test of the platform once a year, and Enterprise customers can read the executive summary of its results.",
         "Critical vulnerabilities found by the test are fixed within 7 days, and high-severity ones within 30 days."],
        ["Customers choose where their data is stored.",
         "Enterprise customers can pick any of the 14 regions, Team customers can pick from 3 regions in their continent, and Basic accounts are placed in the region closest to the account owner."],
    ]),
    (1, "Billing", []),
    (2, "Prices and invoices", [
        ["Basic costs $12 per user per month, Team costs $29 per user per month and Enterprise costs $58 per user per month.",
         "Prices are in US dollars and exclude taxes, which are added at checkout based on the billing address."],
        ["Invoices are issued on the first day of each month and are due within 30 days.",
         "Basic accounts pay by card only, Team accounts can pay by card or invoice, and Enterprise accounts can also pay by purchase order.",
         "Payments received more than 15 days late incur a charge of 1.5% of the amount due."],
    ]),
    (2, "Discounts, overages and credits", [
        ["Annual prepayment earns a discount of 10% on Team and 15% on Enterprise.",
         "Basic is not discounted, and multi-year Enterprise contracts lock the per-user price for the full term."],
        ["Storage beyond the included amount costs $0.021 per GB per month, and egress beyond the included bandwidth costs $0.05 per GB.",
         "Usage alerts at 80% and 100% of each allowance are sent to the account owner so that charges are never a surprise."],
        ["If monthly availability falls below 99.9%, Team customers receive a service credit of 10% of that month's fee.",
         "If it falls below 99.99%, Enterprise customers receive a credit of 25%.",
         "Credits must be requested within 30 days of the end of the affected month and are applied to the next invoice."],
        ["Cancellations require 30 days' written notice on monthly contracts.",
         "Annual contracts end on their anniversary date and are not refunded for the unused remainder of the term."],
        ["Questions about this document can be sent to plans@northwind.example."],
    ]),
]

PLANS_FACTS = [
    ("How long are backups kept on the Enterprise plan?", "Enterprise backups are kept for 365 days; Team backups for 90 days; Basic for 30 days."),
    ("How often are Enterprise databases backed up?", "Basic databases are backed up once a day, Team databases every 12 hours and Enterprise databases every 6 hours."),
    ("How long can a deleted resource be recovered on the Team plan?", "A deleted resource can be recovered for 7 days on Basic, 14 days on Team and 30 days on Enterprise."),
    ("How long does Northwind keep data after an account is closed?", "When an account is closed, Northwind keeps its data for 60 days so that the owner can export it."),
    ("What is the charge for paying an invoice late?", "Payments received more than 15 days late incur a charge of 1.5% of the amount due."),
    ("How long is the free trial of the Team plan?", "A 30-day trial of the Team plan is available to every new account."),
    ("How much does extra storage cost?", "Storage beyond the included amount costs $0.021 per GB per month, and egress beyond the included bandwidth costs $0.05 per GB."),
    ("How quickly are critical vulnerabilities fixed?", "Critical vulnerabilities found by the test are fixed within 7 days, and high-severity ones within 30 days."),
    ("How much notice do I need to cancel a monthly contract?", "Cancellations require 30 days' written notice on monthly contracts."),
    ("How quickly does revoking a customer-managed key make the data unreadable?", "Enterprise customers can supply their own encryption keys, which they can revoke at any time; revoking a key makes the data unreadable within 15 minutes."),
    ("What hours is support available on the Team plan?", "Team and Basic requests are handled between 06:00 and 20:00 UTC on weekdays, and requests that arrive outside those hours wait until the next working morning."),
    ("How often does the technical account manager hold a review call?", "Each Enterprise account has a named technical account manager who holds a review call every quarter, covering usage, incidents and upcoming product changes."),
    ("What discount does annual prepayment give on the Team plan?", "Annual prepayment earns a discount of 10% on Team and 15% on Enterprise."),
    ("How many regions can Team customers choose from for their data?", "Enterprise customers can pick any of the 14 regions, Team customers can pick from 3 regions in their continent, and Basic accounts are placed in the region closest to the account owner."),
]
PLANS_TABLE_QUESTIONS = ["What does Table 3 compare?", "Which table shows how the plans differ?", "What is Table 3 about?"]

# ---------------------------------------------------------------------------------------------
# Document 2: Trailhead Outfitters regional sales (docx -> pdf)
# ---------------------------------------------------------------------------------------------
SALES_HEADER = ["Product", "Region", "Q1", "Q2", "Q3", "Q4", "Total"]
SALES_CAPTION = "Table 1: Units sold by product, region and quarter"
SALES_HEADING = "Sales detail"
PRODUCTS = {  # product: popularity weight
    "Trail Shoes": 1.6, "Rain Shell Jacket": 1.3, "Down Sleeping Bag": 0.9, "Two-Person Tent": 0.7, "Trekking Poles": 1.1,
    "Hydration Pack": 1.2, "Camp Stove": 0.8, "Headlamp": 1.5, "Wool Base Layer": 1.0, "Insulated Bottle": 1.4,
    "Daypack 28L": 1.2, "Water Filter": 0.6, "Climbing Harness": 0.5, "Gaiters": 0.4, "Fleece Pullover": 1.1,
}
REGIONS = {"Northeast": 1.0, "Southeast": 0.8, "Midwest": 0.9, "Mountain": 1.1, "Pacific": 1.5, "Southwest": 0.6}
SEASON = [0.75, 1.0, 1.15, 1.35]


def sales_rows():
    rng, used, rows = random.Random(2025), set(), []
    for product, pw in PRODUCTS.items():
        for region, rw in REGIONS.items():
            quarters = []
            for s in SEASON:
                n = max(20, round(300 * pw * rw * s * rng.uniform(0.8, 1.2)))
                while n in used:  # every number in the table is distinct
                    n += 1
                used.add(n)
                quarters.append(n)
            while sum(quarters) in used:
                quarters[3] += 1
                used.add(quarters[3])
            used.add(sum(quarters))
            rows.append([product, region, *map(str, quarters), f"{sum(quarters):,}"])
    return rows


def sales_sections(rows):
    q = lambda r, i: int(r[i].replace(",", ""))
    total = sum(q(r, 6) for r in rows)
    by = lambda col, names: sorted(((sum(q(r, 6) for r in rows if r[col] == n), n) for n in names), reverse=True)
    products, regions = by(0, PRODUCTS), by(1, REGIONS)
    quarters = sorted(((sum(q(r, i) for r in rows), f"Q{i - 1}") for i in range(2, 6)), reverse=True)
    sections = [
        (1, "Summary", [
            [f"Trailhead Outfitters sold {total:,} units across its 15 products and 6 regions in 2025.",
             f"{products[0][1]} was the best-selling product with {products[0][0]:,} units, and {products[-1][1]} sold the fewest, with {products[-1][0]:,} units.",
             f"{regions[0][1]} was the strongest region with {regions[0][0]:,} units, ahead of {regions[1][1]} with {regions[1][0]:,} units.",
             f"The strongest quarter was {quarters[0][1]}, with {quarters[0][0]:,} units, and the weakest was {quarters[-1][1]}, with {quarters[-1][0]:,} units."],
            ["Online orders accounted for 31% of all units, up from 26% in 2024.",
             "The company ended the year with 74 stores across the six regions.",
             "The Pacific region operates 19 stores, more than any other region.",
             "The Midwest region has 14 stores, the Northeast 12, the Southeast 11, and the Mountain and Southwest regions 9 each."],
        ]),
        (1, "Notes on the figures", [
            ["Units are counted at the point of sale for stores and at the dispatch date for online orders.",
             "Returns are not deducted from the quarter in which the sale was recorded; they are reported separately in the finance pack."],
            ["The Mountain region covers Colorado, Utah and Wyoming.",
             "Figures for the Mountain region include the Boulder pop-up store, which traded from 1 June to 30 September 2025 and is not counted among the 9 permanent stores."],
            ["Camp Stove sales in the fourth quarter include a promotion that ran from 24 to 30 November 2025.",
             "Headlamp units combine the 350 lumen and 600 lumen models, which are reported as one product.",
             "Totals are the sum of the four quarters and are reconciled to the finance system every January."],
        ]),
        (1, SALES_HEADING, []),
        "TABLE",
        (None, None, [
            ["Product managers should use Table 1 when setting purchase quantities for 2026.",
             "Questions about the figures can be sent to the sales operations team, who maintain the source data and publish a revised version if any totals change.",
             "The next regional report covers the first half of 2026 and will be published in August 2026."],
        ]),
    ]
    facts = [
        ("How many units did Trailhead Outfitters sell in 2025?", sections[0][2][0][0]),
        ("Which product sold the most units in 2025?", sections[0][2][0][1]),
        ("Which region was the strongest in 2025?", sections[0][2][0][2]),
        ("Which quarter had the most unit sales?", sections[0][2][0][3]),
        ("What share of units were sold online?", "Online orders accounted for 31% of all units, up from 26% in 2024."),
        ("How many stores does the Pacific region operate?", "The Pacific region operates 19 stores, more than any other region."),
        ("When are online orders counted as sold?", "Units are counted at the point of sale for stores and at the dispatch date for online orders."),
        ("Are returns deducted from the sales figures?", "Returns are not deducted from the quarter in which the sale was recorded; they are reported separately in the finance pack."),
        ("Which states does the Mountain region cover?", "The Mountain region covers Colorado, Utah and Wyoming."),
        ("Which temporary store is included in the Mountain region figures?", "Figures for the Mountain region include the Boulder pop-up store, which traded from 1 June to 30 September 2025 and is not counted among the 9 permanent stores."),
        ("When did the Camp Stove promotion run?", "Camp Stove sales in the fourth quarter include a promotion that ran from 24 to 30 November 2025."),
        ("When will the next regional report be published?", "The next regional report covers the first half of 2026 and will be published in August 2026."),
        ("How are the totals checked?", "Totals are the sum of the four quarters and are reconciled to the finance system every January."),
    ]
    return sections, facts


SALES_TABLE_QUESTIONS = [
    "What does Table 1 show?", "Where can I find units sold by product and region?",
    "Which table has quarterly unit sales?", "What is Table 1 about?",
]


# ---------------------------------------------------------------------------------------------
def build_docx(path, title, sections, header, rows, caption, widths, font_pt):
    d = docx.Document()
    d.core_properties.created = d.core_properties.modified = datetime(2026, 1, 1)
    d.core_properties.author = "Documents for chunking experiment"
    d.add_heading(title, level=0)
    for section in sections:
        if section == "TABLE":
            d.add_paragraph(caption, style="Caption")
            table = d.add_table(rows=1 + len(rows), cols=len(header), style="Table Grid")
            table.autofit = False
            for column, width in zip(table.columns, widths):
                column.width = Inches(width)
            for r, cells in enumerate([header, *rows]):
                for c, text in enumerate(cells):
                    cell = table.cell(r, c)
                    cell.width = Inches(widths[c])
                    para = cell.paragraphs[0]
                    para.paragraph_format.space_after = Pt(0)
                    para.paragraph_format.line_spacing = 1.0
                    run = para.add_run(text)
                    run.font.size = Pt(font_pt)
                    run.bold = r == 0
            continue
        level, heading, paragraphs = section
        if heading:
            d.add_heading(heading, level=level)
        for sentences in paragraphs:
            d.add_paragraph(" ".join(sentences))
    d.save(path)


def pdf_report(path, rows, caption, header):
    pdf = pdfium.PdfDocument(str(path))
    pages = [" ".join(p.get_textpage().get_text_range().split()) for p in pdf]
    per_page = [sum(f"{r[0]} {r[1]} {r[2]} " in text for r in rows) for text in pages]
    print(f"{path.name}: {len(pages)} pages, rows per page {per_page}, header text appears {sum(t.count(' '.join(header)) for t in pages)}x, caption {sum(t.count(caption) for t in pages)}x")
    return pages


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    assert not any("Enterprise" in c for r in PLANS_ROWS for c in r), "header labels must not occur inside rows"
    rows = sales_rows()
    sales, sales_facts = sales_sections(rows)

    build_docx(DATA / "northwind_service_plans.docx", "Northwind Cloud: Service Plans 2026", PLANS_SECTIONS,
               PLANS_HEADER, PLANS_ROWS, PLANS_CAPTION, [2.1, 1.3, 1.5, 1.6], 10)
    build_docx(DATA / "trailhead_regional_sales.docx", "Trailhead Outfitters: Regional Sales 2025", sales,
               SALES_HEADER, rows, SALES_CAPTION, [1.8, 1.1, 0.6, 0.6, 0.6, 0.6, 0.8], 10)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(DATA), str(DATA / "trailhead_regional_sales.docx")],
                   check=True, capture_output=True)

    feature = [{"row": i, "question": text.format(plan=plan)}
               for label, text in PLANS_FEATURE_QUESTIONS for i, r in enumerate(PLANS_ROWS) if r[0] == label
               for plan in PLANS_HEADER[1:]]
    number = [{"row": i, "column": 2 + q, "question": f"How many {r[0]} units were sold in the {r[1]} region in Q{q + 1}?"}
              for i, r in enumerate(rows) for q in range(4)]
    truth = {
        "northwind_service_plans.docx": {
            "header": PLANS_HEADER, "rows": PLANS_ROWS, "caption": PLANS_CAPTION, "heading": PLANS_HEADING,
            "row_pattern": "plan feature", "row_questions": feature,
            "facts": [{"question": q, "sentence": s} for q, s in PLANS_FACTS], "table_questions": PLANS_TABLE_QUESTIONS,
        },
        "trailhead_regional_sales.pdf": {
            "header": SALES_HEADER, "rows": rows, "caption": SALES_CAPTION, "heading": SALES_HEADING,
            "row_pattern": "number lookup", "row_questions": number,
            "facts": [{"question": q, "sentence": s} for q, s in sales_facts], "table_questions": SALES_TABLE_QUESTIONS,
        },
    }
    (DATA / "truth.json").write_text(json.dumps(truth, indent=1, ensure_ascii=False))

    # Checks: every fact sentence is in the document text; the sales table spans 3 pages with its header once.
    plans_text = " ".join(" ".join(p.text.split()) for p in docx.Document(str(DATA / "northwind_service_plans.docx")).paragraphs)
    print(f"northwind_service_plans.docx: {len(plans_text)} text characters, {len(PLANS_ROWS)} table rows")
    pages = pdf_report(DATA / "trailhead_regional_sales.pdf", rows, SALES_CAPTION, SALES_HEADER)
    sales_text = " ".join(pages)
    for name, text, facts in [("plans", plans_text, PLANS_FACTS), ("sales", sales_text, sales_facts)]:
        missing = [s for _, s in facts if s not in text]
        assert not missing, f"{name}: facts not found in the document text: {missing}"
