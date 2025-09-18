# pip install reportlab qrcode[pil]
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Image, Table, TableStyle, KeepInFrame
)
from datetime import date
from io import BytesIO
import qrcode
import os

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
LANDING_URL  = "https://apschram.github.io/curriculum-vitae/"     # QR points here
PDF_URL      = "https://apschram.github.io/curriculum-vitae/Alexander_Schram_CV.pdf"
LINKEDIN_URL = "https://www.linkedin.com/in/alexander-schram-17ab6265/"
GITHUB_URL   = "https://github.com/apschram/curriculum-vitae"

OUTPUT_PDF   = "Alexander_Schram_CV.pdf"
ACCENT       = colors.HexColor("#0B7A75")
BASE_FONT    = "Helvetica"
BOLD_FONT    = "Helvetica-Bold"

# Optional headshot (square works best). Leave as None to skip.
HEADSHOT_PATH = None  # e.g. "AS.png"

# -------------------------------------------------------------------
# CONTENT
# -------------------------------------------------------------------
DATA = {
    "name": "Alexander Pieter Schram",
    "title": "Sports Analytics · Tracking & Modeling",
    "location": "Amsterdam, NL",
    "email": "apschram@gmail.com",
    "phone": "+31 6 52 36 73 57",

    "summary": (
        "Sports data leader focused on tracking analytics, model design, and delivery. "
        "Built end-to-end pipelines and coach-facing tools; values reproducibility and measurable impact."
    ),

    "experience": [
        {
            "company": "PFF",
            "role": "Sr. Manager Team Services & Analysis",
            "dates": "2021–present",
            "bullets": [
                "Led analytics delivery for pro clubs across recruitment and performance.",
                "Built tracking×event fusion workflows and physical metrics reporting.",
                "Improved comms through concise visuals and field-relevant language."
            ],
        },
        {
            "company": "FC Cincinnati",
            "role": "Director of Analytics & Strategy",
            "dates": "2019–2021",
            "bullets": [
                "Built the analytics function across player evaluation and match analysis.",
                "Delivered coach-facing products and recruitment decision support."
            ],
        },
        {
            "company": "remiqz",
            "role": "Manager Data Science & Lead Developer",
            "dates": "2017–2019",
            "bullets": [
                "Led data science projects and productized analytics pipelines."
            ],
        },
        {
            "company": "Hypercube",
            "role": "Consultant",
            "dates": "2014–2017",
            "bullets": [
                "Delivered modeling and analysis for sports/business problems."
            ],
        },
        {
            "company": "Veneficus",
            "role": "Data Intern",
            "dates": "2013",
            "bullets": [
                "Supported data preparation and early-stage modeling."
            ],
        },
        {
            "company": "University of Amsterdam",
            "role": "Research Assistant",
            "dates": "2011–2013",
            "bullets": [
                "Quantitative research support and analysis."
            ],
        },
    ],

    "tech": (
        "Python (pandas, scikit-learn, xgboost), SQL, R, Matplotlib, Shiny, Kalman filters, "
        "ETL, model validation/MAER, experiment design"
    ),
    "providers": (
        "Event: PFF, StatsBomb, Wyscout, Opta, InStat · "
        "Tracking: Second Spectrum, ChyronHego, SkillCorner, Sportlogiq · "
        "GPS: STATSports, Catapult"
    ),
    "education": [
        "MSc Econometrics: Free Track — University of Amsterdam (2014)",
        "BSc Econometrics & Operations Research — University of Amsterdam (2013)"
    ],
    "languages": "Dutch (native), English (C2)",
    "links": {
        "PDF": PDF_URL,
        "LinkedIn": LINKEDIN_URL,
        "GitHub": GITHUB_URL,
    }
}

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def make_qr(url: str, box_size=6) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(BASE_FONT, 8)
    canvas.setFillColor(colors.grey)
    today = date.today().strftime("%Y.%m.%d")
    left = f"Generated with Python — v{today}"
    right = "© Alexander Schram"
    canvas.drawString(18*mm, 12*mm, left)
    canvas.drawRightString(A4[0]-18*mm, 12*mm, right)
    canvas.restoreState()

# -------------------------------------------------------------------
# BUILD
# -------------------------------------------------------------------
def build_pdf(path: str = OUTPUT_PDF):
    styles = getSampleStyleSheet()

    # Use unique names so we don’t collide with built-in styles
    styles.add(ParagraphStyle(name="NameLine",   fontName=BOLD_FONT, fontSize=20, leading=23))
    styles.add(ParagraphStyle(name="SubLine",    fontName=BASE_FONT, fontSize=11, leading=14, textColor=colors.grey))
    styles.add(ParagraphStyle(name="H2Accent",   fontName=BOLD_FONT, fontSize=12.5, leading=16, spaceBefore=8, spaceAfter=4, textColor=ACCENT))
    styles.add(ParagraphStyle(name="BodyMain",   fontName=BASE_FONT, fontSize=10.5, leading=14))  # <- renamed
    styles.add(ParagraphStyle(name="BulletItem", fontName=BASE_FONT, fontSize=10.5, leading=14, leftIndent=10, bulletIndent=0))
    styles.add(ParagraphStyle(name="SmallNote",  fontName=BASE_FONT, fontSize=9.5, leading=12, textColor=colors.grey))

    margin = 18*mm
    frame = Frame(margin, margin, A4[0]-2*margin, A4[1]-2*margin, id="frame")
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)
    doc.addPageTemplates(PageTemplate(id="page", frames=[frame], onPage=footer))

    story = []

    # Header: name, title, contacts/links (left) + QR (+ optional headshot) (right)
    name_p  = Paragraph(DATA["name"], styles["NameLine"])
    title_p = Paragraph(DATA["title"], styles["SubLine"])

    parts = []
    if DATA.get("email"):    parts.append(f'<link href="mailto:{DATA["email"]}">{DATA["email"]}</link>')
    if DATA.get("phone"):    parts.append(DATA["phone"])
    if DATA.get("location"): parts.append(DATA["location"])
    for label, url in DATA.get("links", {}).items():
        if url:
            parts.append(f'<link href="{url}">{label}</link>')
    contact_p = Paragraph(" · ".join(parts), styles["BodyMain"])

    left_stack = [name_p, title_p, Spacer(1, 2*mm), contact_p]
    left_flow  = KeepInFrame(0, 0, left_stack, hAlign="LEFT")

    # QR links to the landing page
    qr_img_bio = make_qr(LANDING_URL)
    qr_img = Image(qr_img_bio, width=28*mm, height=28*mm)

    right_cells = [[qr_img]]
    if HEADSHOT_PATH and os.path.exists(HEADSHOT_PATH):
        right_cells += [[Spacer(1, 2*mm)], [Image(HEADSHOT_PATH, width=28*mm, height=28*mm)]]

    right_tbl = Table(right_cells, colWidths=[30*mm])
    right_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN',  (0,0), (-1,-1), 'RIGHT'),
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
    ]))

    header_row = Table([[left_flow, right_tbl]], colWidths=[None, 30*mm])
    header_row.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
    ]))

    story += [header_row, Spacer(1, 6*mm)]

    # Summary
    if DATA.get("summary"):
        story += [
            Paragraph("Summary", styles["H2Accent"]),
            Paragraph(DATA["summary"], styles["BodyMain"]),
            Spacer(1, 3*mm)
        ]

    # Experience
    story.append(Paragraph("Experience", styles["H2Accent"]))
    for job in DATA["experience"]:
        head = f"<b>{job['company']} — {job['role']} ({job['dates']})</b>"
        story.append(Paragraph(head, styles["BodyMain"]))
        for b in job.get("bullets", []):
            story.append(Paragraph(f"• {b}", styles["BulletItem"]))
        story.append(Spacer(1, 1*mm))

    # Two-column block: Tech/Education vs Languages/Providers
    left_col = [
        Paragraph("Technical", styles["H2Accent"]),
        Paragraph(DATA["tech"], styles["BodyMain"]),
        Spacer(1, 2*mm),
        Paragraph("Education", styles["H2Accent"]),
        *[Paragraph(item, styles["BodyMain"]) for item in DATA["education"]],
    ]
    right_col = [
        Paragraph("Languages", styles["H2Accent"]),
        Paragraph(DATA["languages"], styles["BodyMain"]),
        Spacer(1, 2*mm),
        Paragraph("Data Providers", styles["H2Accent"]),
        Paragraph(DATA["providers"], styles["BodyMain"]),
    ]

    left_kif  = KeepInFrame(0, 0, left_col,  hAlign="LEFT")
    right_kif = KeepInFrame(0, 0, right_col, hAlign="LEFT")

    two_col = Table([[left_kif, right_kif]], colWidths=[None, None])
    two_col.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
    ]))

    story += [Spacer(1, 4*mm), two_col, Spacer(1, 6*mm)]
    story += [Paragraph("Generated with Python — links above for PDF · GitHub · LinkedIn.", styles["SmallNote"])]

    doc.build(story)

if __name__ == "__main__":
    build_pdf(OUTPUT_PDF)
