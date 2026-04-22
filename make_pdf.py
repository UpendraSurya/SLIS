"""Generate SLIS Project Report PDF using ReportLab."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.colors import HexColor
from datetime import date

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK   = HexColor("#0f172a")
ACCENT    = HexColor("#4F7FFF")
ACCENT_LT = HexColor("#8FB3FF")
TEXT_MAIN = HexColor("#1e293b")
TEXT_SUB  = HexColor("#475569")
TEXT_MONO = HexColor("#334155")
LOW_GREEN = HexColor("#16a34a")
MED_AMB   = HexColor("#d97706")
HIGH_RED  = HexColor("#dc2626")
ROW_ALT   = HexColor("#f1f5f9")
BORDER    = HexColor("#cbd5e1")
HEADER_BG = HexColor("#1e40af")

W, H = A4

# ── Styles ────────────────────────────────────────────────────────────────────
SS = getSampleStyleSheet()

def style(name, **kw):
    base = SS["Normal"]
    return ParagraphStyle(name, parent=base, **kw)

S = {
    "cover_title": style("ct", fontSize=32, fontName="Helvetica-Bold",
                         textColor=colors.white, leading=40, alignment=TA_CENTER),
    "cover_sub":   style("cs", fontSize=14, fontName="Helvetica",
                         textColor=HexColor("#93c5fd"), leading=20, alignment=TA_CENTER),
    "cover_tag":   style("ctg", fontSize=10, fontName="Helvetica",
                         textColor=HexColor("#64748b"), alignment=TA_CENTER),
    "h1":          style("h1", fontSize=16, fontName="Helvetica-Bold",
                         textColor=ACCENT, leading=22, spaceBefore=18, spaceAfter=6),
    "h2":          style("h2", fontSize=12, fontName="Helvetica-Bold",
                         textColor=TEXT_MAIN, leading=16, spaceBefore=12, spaceAfter=4),
    "body":        style("body", fontSize=10, fontName="Helvetica",
                         textColor=TEXT_MAIN, leading=16, alignment=TA_JUSTIFY,
                         spaceBefore=4, spaceAfter=4),
    "bullet":      style("bul", fontSize=10, fontName="Helvetica",
                         textColor=TEXT_MAIN, leading=15, leftIndent=16,
                         spaceBefore=2, spaceAfter=2, bulletIndent=6),
    "mono":        style("mono", fontSize=9, fontName="Courier",
                         textColor=TEXT_MONO, leading=14, spaceBefore=2, spaceAfter=2),
    "caption":     style("cap", fontSize=8, fontName="Helvetica",
                         textColor=TEXT_SUB, leading=12, alignment=TA_CENTER),
    "th":          style("th", fontSize=9, fontName="Helvetica-Bold",
                         textColor=colors.white, leading=13, alignment=TA_CENTER),
    "td":          style("td", fontSize=9, fontName="Helvetica",
                         textColor=TEXT_MAIN, leading=13),
    "td_c":        style("tdc", fontSize=9, fontName="Helvetica",
                         textColor=TEXT_MAIN, leading=13, alignment=TA_CENTER),
    "td_mono":     style("tdm", fontSize=8, fontName="Courier",
                         textColor=TEXT_MONO, leading=12),
    "label":       style("lbl", fontSize=8, fontName="Helvetica-Bold",
                         textColor=TEXT_SUB, leading=12, spaceBefore=10),
    "metric_big":  style("mb", fontSize=22, fontName="Helvetica-Bold",
                         textColor=ACCENT, leading=26, alignment=TA_CENTER),
    "metric_lbl":  style("ml", fontSize=8, fontName="Helvetica",
                         textColor=TEXT_SUB, leading=11, alignment=TA_CENTER),
    "challenge_h": style("ch", fontSize=11, fontName="Helvetica-Bold",
                         textColor=HIGH_RED, leading=15, spaceBefore=8, spaceAfter=2),
    "section_tag": style("st", fontSize=8, fontName="Helvetica-Bold",
                         textColor=ACCENT, leading=12, spaceBefore=14, spaceAfter=2),
}

# ── Table helpers ─────────────────────────────────────────────────────────────
def make_table(data, col_widths, header=True, zebra=True):
    rows = [[Paragraph(str(c), S["th"] if i == 0 and header else S["td_c"])
             if isinstance(c, str) else c
             for c in row]
            for i, row in enumerate(data)]

    style_cmds = [
        ("BACKGROUND",  (0, 0), (-1, 0 if not header else 0), HEADER_BG if header else ROW_ALT),
        ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1),
         [colors.white, ROW_ALT] if zebra else [colors.white]),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]
    return Table(rows, colWidths=col_widths,
                 style=TableStyle(style_cmds), hAlign="LEFT")


def td(text, style_name="td", **kw):
    return Paragraph(str(text), S[style_name])


def section_rule():
    return HRFlowable(width="100%", thickness=1, color=HexColor("#e2e8f0"),
                      spaceBefore=4, spaceAfter=4)


# ── Cover page ────────────────────────────────────────────────────────────────
def cover_page():
    elems = []
    elems.append(Spacer(1, 3.5*cm))

    # Dark banner
    banner_data = [[Paragraph("SLIS", S["cover_title"])]]
    banner = Table(banner_data, colWidths=[W - 4*cm],
                   style=TableStyle([
                       ("BACKGROUND", (0,0), (-1,-1), BG_DARK),
                       ("TOPPADDING",    (0,0), (-1,-1), 28),
                       ("BOTTOMPADDING", (0,0), (-1,-1), 12),
                       ("LEFTPADDING",   (0,0), (-1,-1), 24),
                       ("RIGHTPADDING",  (0,0), (-1,-1), 24),
                       ("ROUNDEDCORNERS", [8]),
                   ]))
    elems.append(banner)
    elems.append(Spacer(1, 0.3*cm))

    subtitle_data = [[Paragraph("Student Learning Intelligence System", S["cover_sub"])]]
    subtitle = Table(subtitle_data, colWidths=[W - 4*cm],
                     style=TableStyle([
                         ("BACKGROUND", (0,0), (-1,-1), HexColor("#1e293b")),
                         ("TOPPADDING",    (0,0), (-1,-1), 10),
                         ("BOTTOMPADDING", (0,0), (-1,-1), 10),
                         ("ROUNDEDCORNERS", [8]),
                     ]))
    elems.append(subtitle)
    elems.append(Spacer(1, 1*cm))

    elems.append(Paragraph("PROJECT REPORT", S["cover_tag"]))
    elems.append(Spacer(1, 0.6*cm))

    # Metric strip
    metrics = [
        ("500", "Students"),
        ("92%", "Model Accuracy"),
        ("0.885", "R² Score"),
        ("9", "API Endpoints"),
    ]
    row = []
    for val, lbl in metrics:
        cell = [Paragraph(val, S["metric_big"]), Paragraph(lbl, S["metric_lbl"])]
        row.append(cell)

    metric_table_data = [[
        Table([[Paragraph(v, S["metric_big"])],[Paragraph(l, S["metric_lbl"])]],
              colWidths=[3.5*cm],
              style=TableStyle([
                  ("BACKGROUND", (0,0), (-1,-1), ROW_ALT),
                  ("TOPPADDING", (0,0), (-1,-1), 10),
                  ("BOTTOMPADDING", (0,0), (-1,-1), 10),
                  ("ROUNDEDCORNERS", [6]),
              ]))
        for v, l in metrics
    ]]
    metric_strip = Table(metric_table_data,
                         colWidths=[3.5*cm]*4,
                         hAlign="CENTER",
                         style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                                           ("LEFTPADDING",(0,0),(-1,-1),4),
                                           ("RIGHTPADDING",(0,0),(-1,-1),4)]))
    elems.append(metric_strip)
    elems.append(Spacer(1, 1.5*cm))

    # Tech badges
    tech = ["FastAPI", "scikit-learn", "React 18", "Random Forest", "Ridge Regression", "HuggingFace"]
    badge_cells = []
    for t in tech:
        badge_cells.append(
            Table([[Paragraph(t, style("b", fontSize=8, fontName="Helvetica-Bold",
                                       textColor=ACCENT, alignment=TA_CENTER))]],
                  style=TableStyle([
                      ("BACKGROUND", (0,0), (-1,-1), HexColor("#eff6ff")),
                      ("TOPPADDING", (0,0), (-1,-1), 4),
                      ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                      ("LEFTPADDING", (0,0), (-1,-1), 8),
                      ("RIGHTPADDING", (0,0), (-1,-1), 8),
                      ("BOX", (0,0), (-1,-1), 0.5, ACCENT),
                      ("ROUNDEDCORNERS", [10]),
                  ]))
        )

    badge_row = Table([badge_cells], hAlign="CENTER",
                      style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                                        ("LEFTPADDING",(0,0),(-1,-1),3),
                                        ("RIGHTPADDING",(0,0),(-1,-1),3)]))
    elems.append(badge_row)
    elems.append(Spacer(1, 3*cm))

    elems.append(Paragraph(f"Date: {date.today().strftime('%B %d, %Y')}", S["caption"]))
    elems.append(Paragraph("github.com/UpendraSurya/SLIS", S["caption"]))
    elems.append(PageBreak())
    return elems


# ── Section 1: Problem Statement ─────────────────────────────────────────────
def section_problem():
    elems = []
    elems.append(Paragraph("01", S["section_tag"]))
    elems.append(Paragraph("Problem Statement", S["h1"]))
    elems.append(section_rule())
    elems.append(Paragraph(
        "Academic institutions struggle to identify at-risk students early enough to intervene "
        "effectively. By the time poor performance becomes visible through final exam results, "
        "it is often too late to provide meaningful support. Educators lack a centralised, "
        "data-driven tool to monitor individual student performance trends, detect risk using "
        "early-semester signals, and deliver personalised guidance at scale.", S["body"]))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("The absence of such a system leads to:", S["body"]))
    for pt in [
        "Preventable student failures due to late detection",
        "Delayed interventions — support arrives after the damage is done",
        "Inability to direct limited faculty time toward students who need it most",
        "No data-driven feedback loop for students to self-correct during the semester",
    ]:
        elems.append(Paragraph(f"• {pt}", S["bullet"]))
    return elems


# ── Section 2: Objective ──────────────────────────────────────────────────────
def section_objective():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("02", S["section_tag"]))
    elems.append(Paragraph("Objective", S["h1"]))
    elems.append(section_rule())
    objectives = [
        ("Predict student risk level", "Classify each student as Low / Medium / High risk using early-semester data — before the final exam."),
        ("Forecast final score", "Predict the weighted score (IT1×0.25 + IT2×0.25 + Final×0.50) so students have a concrete performance target."),
        ("AI recommendations", "Generate 4 personalised, priority-tagged recommendations per student using Qwen3-32B."),
        ("Teacher Portal", "Cohort dashboard, student directory, inline mark editing, CSV/Excel score upload."),
        ("Student Portal", "Personal risk tracker, performance breakdown, attendance trend, AI recommendations."),
        ("Live score ingestion", "Upload exam sheets as CSV/Excel — scores update in memory and persist to disk instantly."),
    ]
    data = [[td("Objective", "th"), td("Description", "th")]]
    for obj, desc in objectives:
        data.append([td(obj, "td"), td(desc, "td")])
    elems.append(make_table(data, [5*cm, 11*cm]))
    return elems


# ── Section 3: Approach ───────────────────────────────────────────────────────
def section_approach():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("03", S["section_tag"]))
    elems.append(Paragraph("Approach / Methodology", S["h1"]))
    elems.append(section_rule())

    phases = [
        ("Phase 1", "Data Generation",
         "500 synthetic students generated across 7 behavioural archetypes (Consistent, Late Bloomer, "
         "Early Bird, Struggle, Comeback, Exam Ace, Final Burnout) to simulate realistic academic patterns."),
        ("Phase 2", "Feature Engineering",
         "18–20 features built: attendance monthly values + trend slope, IT1/IT2 averages + delta + "
         "slope + rolling windows (W4, W8) + std/range per subject, LMS engagement composite score, GPA."),
        ("Phase 3", "Risk Labelling (No Leakage)",
         "Labels derived from IT1+IT2 percentiles (p33/p66) only. Final exam excluded to prevent "
         "data leakage — the model predicts risk before the final exam happens."),
        ("Phase 4", "Model Training",
         "5-fold cross-validation across multiple algorithms. Random Forest selected for risk "
         "classification (F1=96.2%). Ridge Regression selected for score prediction (R²=0.885). "
         "class_weight='balanced' applied for imbalance handling."),
        ("Phase 5", "Backend API",
         "FastAPI REST API with 9 endpoints. DataStore loads CSVs into memory at startup. "
         "Models loaded once via joblib. All endpoints return JSON with Pydantic validation."),
        ("Phase 6", "Frontend",
         "Two React 18 SPAs (Teacher + Student portals) using Babel CDN — no build step. "
         "apiFetch() pattern falls back to mock data silently if API is unavailable."),
        ("Phase 7", "Score Upload Pipeline",
         "POST /api/upload/scores accepts CSV/Excel, matches rows by student_id+subject, "
         "updates DataStore in memory, persists back to scores.csv on disk."),
    ]

    for phase, title, desc in phases:
        row_data = [[
            td(phase, "td_mono"),
            td(f"<b>{title}</b>", "td"),
            td(desc, "td"),
        ]]
        t = Table(row_data, colWidths=[2*cm, 4*cm, 10*cm],
                  style=TableStyle([
                      ("BACKGROUND", (0,0), (0,-1), HexColor("#eff6ff")),
                      ("GRID", (0,0), (-1,-1), 0.4, BORDER),
                      ("VALIGN", (0,0), (-1,-1), "TOP"),
                      ("TOPPADDING", (0,0), (-1,-1), 6),
                      ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                      ("LEFTPADDING", (0,0), (-1,-1), 8),
                      ("RIGHTPADDING", (0,0), (-1,-1), 8),
                  ]))
        elems.append(t)
        elems.append(Spacer(1, 2))
    return elems


# ── Section 4: Tools Used ─────────────────────────────────────────────────────
def section_tools():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("04", S["section_tag"]))
    elems.append(Paragraph("Tools Used", S["h1"]))
    elems.append(section_rule())

    tools = [
        ("Python 3.10",       "Primary language",           "Ecosystem richness for data, ML, and web"),
        ("FastAPI",           "REST API backend",           "Auto OpenAPI docs, async, Pydantic validation, fastest Python web framework"),
        ("scikit-learn",      "ML training & inference",    "Consistent API, CV utilities, joblib serialisation"),
        ("pandas / NumPy",    "Data engineering",           "Tabular manipulation, rolling averages, trend slopes"),
        ("joblib",            "Model serialisation",        "Efficient NumPy array storage, scikit-learn standard"),
        ("React 18 (CDN)",    "Frontend UI",                "No build step — single HTML file per portal"),
        ("Babel Standalone",  "JSX transpilation",          "Enables JSX in browser without bundler"),
        ("HuggingFace API",   "AI recommendations",         "Qwen3-32B via API — no local GPU required"),
        ("openpyxl",          "Excel parsing",              "pandas dependency for .xlsx support in upload endpoint"),
        ("uvicorn",           "ASGI server",                "Production server for FastAPI, supports --reload"),
        ("python-dotenv",     "Config management",          "Keeps API tokens out of source code"),
        ("reportlab",         "PDF generation",             "Programmatic PDF with full layout control"),
    ]

    data = [[td("Tool", "th"), td("Purpose", "th"), td("Reason", "th")]]
    for tool, purpose, reason in tools:
        data.append([td(tool, "td_mono"), td(purpose, "td"), td(reason, "td")])

    elems.append(make_table(data, [3.8*cm, 4*cm, 8.2*cm]))
    return elems


# ── Section 5: Dataset ────────────────────────────────────────────────────────
def section_dataset():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("05", S["section_tag"]))
    elems.append(Paragraph("Dataset", S["h1"]))
    elems.append(section_rule())

    elems.append(Paragraph(
        "Fully synthetic dataset generated via <font name='Courier'>data/generate_data.py</font> "
        "to simulate a realistic Indian engineering college cohort. No real student data was used.", S["body"]))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("File Summary", S["h2"]))
    files = [
        ("students.csv",    "500",   "Student demographics, major, GPA"),
        ("scores.csv",      "2,500", "IT1, IT2, final scores (5 subjects × 500 students)"),
        ("attendance.csv",  "2,000", "Monthly attendance % (4 months × 500 students)"),
        ("activity.csv",    "500",   "LMS logins, forum posts, resources, session minutes"),
    ]
    data = [[td("File", "th"), td("Rows", "th"), td("Description", "th")]]
    for f, r, d in files:
        data.append([td(f, "td_mono"), td(r, "td_c"), td(d, "td")])
    elems.append(make_table(data, [5*cm, 2.5*cm, 8.5*cm]))

    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph("Subjects (AI/ML)", S["h2"]))
    subjects = ["Machine Learning", "Deep Learning", "Python for AI",
                "Data Structures & Algorithms", "Statistics for AI"]
    subj_cells = [
        Table([[Paragraph(s, style("sb", fontSize=9, fontName="Helvetica-Bold",
                                   textColor=ACCENT, alignment=TA_CENTER))]],
              style=TableStyle([
                  ("BACKGROUND", (0,0), (-1,-1), HexColor("#eff6ff")),
                  ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                  ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                  ("BOX",(0,0),(-1,-1),0.5,ACCENT),("ROUNDEDCORNERS",[8]),
              ]))
        for s in subjects
    ]
    elems.append(Table([subj_cells], hAlign="LEFT",
                       style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),
                                         ("RIGHTPADDING",(0,0),(-1,-1),3)])))

    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph("Student Archetypes", S["h2"]))
    archetypes = [
        ("Consistent",     "Stable performance throughout semester"),
        ("Late Bloomer",   "Low early scores, strong final exam"),
        ("Early Bird",     "High early scores, drops off later"),
        ("Struggle",       "Consistently low across all assessments"),
        ("Comeback",       "Crisis mid-semester, then recovery"),
        ("Exam Ace",       "Poor internals, dominates final exam"),
        ("Final Burnout",  "Strong internals, collapses at final"),
    ]
    data = [[td("Archetype", "th"), td("Pattern", "th")]]
    for a, p in archetypes:
        data.append([td(a, "td"), td(p, "td")])
    elems.append(make_table(data, [5*cm, 11*cm]))
    return elems


# ── Section 6: Results ────────────────────────────────────────────────────────
def section_results():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("06", S["section_tag"]))
    elems.append(Paragraph("Results / Output", S["h1"]))
    elems.append(section_rule())

    # Big metric cards
    metrics = [
        ("96.2%", "CV F1 Macro",        ACCENT),
        ("92%",   "Test Accuracy",      LOW_GREEN),
        ("0.885", "R² Score",           ACCENT),
        ("4.68",  "Test RMSE (±marks)", MED_AMB),
    ]
    cells = []
    for val, lbl, col in metrics:
        cells.append(
            Table([
                [Paragraph(val, style("mv", fontSize=20, fontName="Helvetica-Bold",
                                      textColor=col, alignment=TA_CENTER))],
                [Paragraph(lbl, S["metric_lbl"])],
            ], colWidths=[3.6*cm],
            style=TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),ROW_ALT),
                ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                ("ROUNDEDCORNERS",[6]),
            ]))
        )
    elems.append(Table([cells], colWidths=[3.6*cm]*4,
                       style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),4),
                                         ("RIGHTPADDING",(0,0),(-1,-1),4)])))

    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph("ML Model Performance", S["h2"]))
    model_data = [
        [td("Model", "th"), td("Task", "th"), td("Algorithm", "th"), td("CV", "th"), td("Test", "th")],
        [td("Risk Classifier", "td"), td("3-class classification", "td"),
         td("Random Forest", "td_mono"),
         td("F1 Macro = 96.2%", "td_c"), td("Accuracy = 92%", "td_c")],
        [td("Score Predictor", "td"), td("Regression (0–100)", "td"),
         td("Ridge Regression", "td_mono"),
         td("RMSE = 5.02", "td_c"), td("RMSE=4.68, R²=0.885", "td_c")],
    ]
    elems.append(make_table(model_data, [4*cm, 4.5*cm, 3.5*cm, 3*cm, 4*cm]))

    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph("API Endpoints Verified", S["h2"]))
    api_data = [
        [td("Method", "th"), td("Endpoint", "th"), td("Description", "th")],
        [td("GET",  "td_c"), td("/health", "td_mono"),                              td("Server + model status", "td")],
        [td("GET",  "td_c"), td("/api/students", "td_mono"),                        td("Paginated list, searchable, filterable by risk", "td")],
        [td("GET",  "td_c"), td("/api/students/{id}", "td_mono"),                   td("Full profile with ML inference", "td")],
        [td("GET",  "td_c"), td("/api/dashboard/stats", "td_mono"),                 td("Cohort-level analytics", "td")],
        [td("GET",  "td_c"), td("/api/model-metrics", "td_mono"),                   td("Live model performance numbers", "td")],
        [td("POST", "td_c"), td("/api/predict", "td_mono"),                         td("Risk + score for any custom inputs", "td")],
        [td("GET",  "td_c"), td("/api/recommendations/{id}", "td_mono"),             td("4 AI-generated recommendations", "td")],
        [td("POST", "td_c"), td("/api/upload/scores", "td_mono"),                   td("CSV/Excel exam score ingestion", "td")],
        [td("PUT",  "td_c"), td("/api/students/{id}/scores/{subject}", "td_mono"),  td("Inline mark correction", "td")],
    ]
    elems.append(make_table(api_data, [1.8*cm, 7*cm, 7.2*cm]))

    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph("Portal Features", S["h2"]))
    portal_data = [
        [td("Portal", "th"), td("Page", "th"), td("Functionality", "th")],
        [td("Teacher", "td"), td("Dashboard", "td"),        td("Risk distribution, model metrics, subject averages, top performers", "td")],
        [td("Teacher", "td"), td("Student Directory", "td"),td("Search by name/ID, filter by risk, paginated (500 students)", "td")],
        [td("Teacher", "td"), td("Student Profile", "td"),  td("Scores, attendance, LMS activity, AI recs, inline mark editor", "td")],
        [td("Teacher", "td"), td("Custom Predict", "td"),   td("Enter metrics → instant risk level + predicted score", "td")],
        [td("Teacher", "td"), td("Upload Scores", "td"),    td("Upload CSV/Excel, preview, update + persist to disk", "td")],
        [td("Student", "td"), td("My Dashboard", "td"),     td("Risk hero banner, predicted score, attendance by month, LMS stats", "td")],
        [td("Student", "td"), td("My Recommendations", "td"),td("AI recs sorted High → Medium → Low", "td")],
        [td("Student", "td"), td("My Performance", "td"),   td("IT1/IT2/Final per subject with improving/declining/stable trend", "td")],
    ]
    elems.append(make_table(portal_data, [2.5*cm, 4*cm, 9.5*cm]))
    return elems


# ── Section 7: Challenges ─────────────────────────────────────────────────────
def section_challenges():
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(Paragraph("07", S["section_tag"]))
    elems.append(Paragraph("Challenges Faced", S["h1"]))
    elems.append(section_rule())

    challenges = [
        ("1. Data Leakage in Risk Labels",
         "Risk labels were initially derived from a score that included the final exam, "
         "causing the classifier to achieve near-perfect accuracy by using future data.",
         "Re-labelled using only IT1+IT2 via percentile thresholds (p33, p66). "
         "Final exam reserved exclusively as the regression target."),
        ("2. Feature Mismatch in Predict Endpoint",
         "The /api/predict route called ml_service.predict_risk() with positional arguments, "
         "but the ML service was refactored to accept a feature dictionary, causing HTTP 500.",
         "Updated route to build a complete feat_dict with all required keys before calling the ML service."),
        ("3. Predicted Score Returning 0.0",
         "The predict form only collects 5 inputs but the model needs 20 features. "
         "Missing features defaulted to 0.0, pushing the regression output toward zero.",
         "Added heuristic imputation — estimated avg_it1/avg_it2 from gpa_start x 10, "
         "defaulted monthly attendance to avg_attendance, set trend/std to 0.0."),
        ("4. GPA Scale Mismatch",
         "PredictRequest schema validated gpa_start as 1.0–4.0 (US scale) but the dataset "
         "uses 0–10 scale (Indian university standard). Valid students were rejected.",
         "Updated schema to ge=0.0, le=10.0 and corrected the frontend form hint."),
        ("5. JSX Files Require HTTP Server",
         "Opening index.html via file:// protocol fails because the browser blocks loading "
         ".jsx files via &lt;script src&gt; due to CORS restrictions on local file paths.",
         "Documented requirement to serve via python3 -m http.server 3000 in README and startup guide."),
        ("6. Subject Name Inconsistency",
         "Frontend mock data used different subject names than the backend CSV. "
         "After renaming to AI/ML subjects, fallback data showed old names.",
         "Renamed all subjects in scores.csv via Python script, "
         "then updated mock data in both TeacherApp.jsx and StudentApp.jsx."),
    ]

    for title, problem, solution in challenges:
        block = [
            Paragraph(title, S["challenge_h"]),
        ]
        row = [[
            Table([[Paragraph("PROBLEM", style("pl", fontSize=7, fontName="Helvetica-Bold",
                                               textColor=HIGH_RED))],
                   [Paragraph(problem, S["body"])]],
                  style=TableStyle([
                      ("BACKGROUND",(0,0),(-1,-1),HexColor("#fff5f5")),
                      ("BOX",(0,0),(-1,-1),0.5,HIGH_RED),
                      ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                      ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                      ("ROUNDEDCORNERS",[4]),
                  ]), colWidths=[7.5*cm]),
            Table([[Paragraph("SOLUTION", style("sl", fontSize=7, fontName="Helvetica-Bold",
                                                textColor=LOW_GREEN))],
                   [Paragraph(solution, S["body"])]],
                  style=TableStyle([
                      ("BACKGROUND",(0,0),(-1,-1),HexColor("#f0fdf4")),
                      ("BOX",(0,0),(-1,-1),0.5,LOW_GREEN),
                      ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                      ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                      ("ROUNDEDCORNERS",[4]),
                  ]), colWidths=[7.5*cm]),
        ]]
        pair = Table(row, colWidths=[7.5*cm, 7.5*cm],
                     style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),
                                       ("RIGHTPADDING",(0,0),(-1,-1),0),
                                       ("VALIGN",(0,0),(-1,-1),"TOP")]))
        block.append(pair)
        elems.append(KeepTogether(block))
        elems.append(Spacer(1, 0.3*cm))
    return elems


# ── Page header / footer ──────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Footer line
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.8*cm, W-2*cm, 1.8*cm)
    # Footer text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(TEXT_SUB)
    canvas.drawString(2*cm, 1.3*cm, "SLIS — Student Learning Intelligence System")
    canvas.drawRightString(W-2*cm, 1.3*cm, f"Page {doc.page}")
    # Header accent bar (skip cover)
    if doc.page > 1:
        canvas.setFillColor(ACCENT)
        canvas.rect(0, H-0.35*cm, W, 0.35*cm, fill=1, stroke=0)
    canvas.restoreState()


# ── Build ─────────────────────────────────────────────────────────────────────
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2.5*cm,
        title="SLIS Project Report",
        author="Jonnalagadda Upendra Surya",
        subject="Student Learning Intelligence System",
    )

    story = (
        cover_page() +
        section_problem() +
        section_objective() +
        section_approach() +
        section_tools() +
        section_dataset() +
        section_results() +
        section_challenges()
    )

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF saved → {output_path}")


if __name__ == "__main__":
    build_pdf("/Users/upendrasuryajonnalagadda/Downloads/SLIS_Project_Report.pdf")
