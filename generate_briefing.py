from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

OUTPUT = "session-3/GROUP4-SESSION3-BRIEFING.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=20*mm,
    bottomMargin=20*mm,
    leftMargin=22*mm,
    rightMargin=22*mm,
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Title"],
    fontSize=22,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=11,
    textColor=colors.HexColor("#555555"),
    spaceAfter=16,
)
h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=14,
    textColor=colors.HexColor("#1a1a2e"),
    spaceBefore=14,
    spaceAfter=6,
)
h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=11,
    textColor=colors.HexColor("#2d6a4f"),
    spaceBefore=10,
    spaceAfter=4,
)
body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontSize=10,
    leading=15,
    textColor=colors.HexColor("#333333"),
    spaceAfter=6,
)
code_style = ParagraphStyle(
    "Code",
    parent=styles["Code"],
    fontSize=11,
    backColor=colors.HexColor("#f0f4f0"),
    borderPadding=(6, 8, 6, 8),
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=8,
    spaceBefore=4,
)
bullet_style = ParagraphStyle(
    "Bullet",
    parent=body_style,
    leftIndent=14,
    bulletIndent=4,
    spaceAfter=3,
)
note_style = ParagraphStyle(
    "Note",
    parent=body_style,
    backColor=colors.HexColor("#fff8e1"),
    borderPadding=(6, 8, 6, 8),
    textColor=colors.HexColor("#555500"),
    fontSize=9.5,
)

stop_style = ParagraphStyle(
    "Stop",
    parent=body_style,
    backColor=colors.HexColor("#fdecea"),
    borderPadding=(8, 10, 8, 10),
    textColor=colors.HexColor("#7a0000"),
    fontSize=10,
    spaceAfter=8,
    spaceBefore=4,
)
strategy_style = ParagraphStyle(
    "Strategy",
    parent=body_style,
    backColor=colors.HexColor("#e8f5e9"),
    borderPadding=(8, 10, 8, 10),
    textColor=colors.HexColor("#1b5e20"),
    fontSize=10,
    spaceAfter=8,
    spaceBefore=4,
)

story = []

# ── Header ──────────────────────────────────────────────────────────────────
story.append(Paragraph("Group 4 — Barcelona Mycorrhizal", title_style))
story.append(Paragraph("Session 3 · CRISP-DM Data Preparation · Team Briefing", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2d6a4f")))
story.append(Spacer(1, 10))

# ── Strategic direction ──────────────────────────────────────────────────────
story.append(Paragraph("Strategic direction — read this first", h1_style))
story.append(Paragraph(
    "<b>STOP.</b> Do not build or improve any frontend, map UI, or visualisation. "
    "The teacher will not review it. The explainer map exists — leave it alone.",
    stop_style,
))
story.append(Paragraph(
    "<b>DO THIS INSTEAD.</b> Show clearly: how you are processing your data, "
    "why you made each decision, and for whom the data is being prepared. "
    "The deliverable is a defensible, documented data pipeline — not a product.",
    strategy_style,
))
story.append(Paragraph("The three questions every notebook must answer:", body_style))
for item in [
    "<b>How?</b> What steps transform raw data into a usable layer (filter, clean, derive, validate)",
    "<b>Why?</b> What design decision drove each step — and what would break if you skipped it",
    "<b>For whom?</b> Urban planners and city ecologists making intervention decisions in Barcelona — someone who needs to trust the numbers, not just see a map",
]:
    story.append(Paragraph(f"• {item}", bullet_style))
story.append(Spacer(1, 6))

# ── What the teacher wants ───────────────────────────────────────────────────
story.append(Paragraph("What the teacher said", h1_style))
story.append(Paragraph(
    "The work is done — the map, the scoring, the connectivity analysis. "
    "What is missing is the <b>documented data preparation process</b>. "
    "The teacher follows CRISP-DM and wants to see, for every dataset:",
    body_style,
))
for item in [
    "How rows were filtered — print counts <b>before and after</b> every filter",
    "Design decisions: which rows belong, which columns matter, why",
    "How missing values were handled: <b>drop / impute / flag / model</b>",
    "Unit standardisation (metres, Celsius, unitless NDVI — all stated explicitly)",
    "Defensive bounds checks (NDVI −1 to 1, LST 15–55 °C, coordinates in Barcelona bbox)",
    "Each team member contributes <b>their own data layer</b> with a full notebook",
]:
    story.append(Paragraph(f"• {item}", bullet_style))

story.append(Spacer(1, 8))

# ── How to get started ───────────────────────────────────────────────────────
story.append(Paragraph("How to get started — activate the task guide", h1_style))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 6))

story.append(Paragraph(
    "The repo has a built-in task guide that prevents two people from working on the same thing. "
    "Open the project in <b>Claude Code</b> and type:",
    body_style,
))
story.append(Paragraph("/tasks-for-mushrooms", code_style))
story.append(Paragraph("Claude will:", body_style))
for item in [
    "Ask your name and save your profile",
    "Show you which tasks are still unclaimed",
    "Let you pick one — your claim is written instantly",
    "Print the full task description so you can start immediately",
]:
    story.append(Paragraph(f"• {item}", bullet_style))

story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Note:</b> Dominika and Juan — your personal data layer tasks (D-DOMINIKA / D-JUAN) "
    "are already pre-claimed to your names. The skill will show them to you first.",
    note_style,
))
story.append(Spacer(1, 10))

# ── Task table ───────────────────────────────────────────────────────────────
story.append(Paragraph("Available tasks at a glance", h1_style))

table_data = [
    ["ID", "Track", "Task", "Pre-assigned"],
    ["P1", "PROCESS", "Retrofit notebook 02 — grid-trees", "—"],
    ["P2", "PROCESS", "Retrofit notebook 03 — scoring", "—"],
    ["P3", "PROCESS", "Retrofit notebook 04 — connectivity", "—"],
    ["P4", "PROCESS", "Retrofit notebook 05 — visualisation", "—"],
    ["P5", "PROCESS", "New validation notebook — bounds assertions", "—"],
    ["D-DOMINIKA", "DATA", "Dominika's personal data layer + notebook", "Dominika"],
    ["D-JUAN", "DATA", "Juan's personal data layer + notebook", "Juan"],
    ["DO1", "DOCS", "Write the Session 3 README", "—"],
    ["DO2", "DOCS", "Restructure data-quality-audit with CRISP-DM framing", "—"],
]

col_widths = [28*mm, 22*mm, 85*mm, 30*mm]
tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
tbl.setStyle(TableStyle([
    # Header row
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
    ("TOPPADDING", (0, 0), (-1, 0), 7),
    # Data rows
    ("FONTSIZE", (0, 1), (-1, -1), 8.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f9f6")]),
    ("TOPPADDING", (0, 1), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    # Pre-assigned column highlight
    ("TEXTCOLOR", (3, 6), (3, 7), colors.HexColor("#2d6a4f")),
    ("FONTNAME", (3, 6), (3, 7), "Helvetica-Bold"),
    # Grid
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#2d6a4f")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(tbl)
story.append(Spacer(1, 10))

# ── Rules ────────────────────────────────────────────────────────────────────
story.append(Paragraph("Rules", h1_style))
for item in [
    "Claim your task <i>before</i> starting — edit <code>session-3/task-ownership.yaml</code> or use the skill",
    "Only Rafik can release a claimed task",
    "Push your work to <b>main</b> when done and set your task status to <code>done</code>",
    "If a task has been claimed 7+ days with no update, flag it to Rafik",
]:
    story.append(Paragraph(f"• {item}", bullet_style))

story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Repo: github.com/dklopotek/group4-data-for-all  ·  Tasks: session-3/tasks.md  ·  Ownership: session-3/task-ownership.yaml",
    ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=colors.HexColor("#888888"), alignment=1),
))

doc.build(story)
print(f"PDF created: {OUTPUT}")
