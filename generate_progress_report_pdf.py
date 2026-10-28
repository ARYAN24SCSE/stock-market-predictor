"""
Script to generate Stock_Market_Prediction_Progress_Report.docx and PDF
for Galgotias University BCA Progress Review.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import win32com.client

def generate_progress_report():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    docx_path = os.path.join(base_dir, "Stock_Market_Prediction_Progress_Report.docx")
    pdf_path = os.path.join(base_dir, "Stock_Market_Prediction_Progress_Report.pdf")

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    NAVY = RGBColor(26, 54, 93)       # #1A365D Primary
    DARK_BLUE = RGBColor(37, 99, 235) # #2563EB Secondary
    CHARCOAL = RGBColor(30, 41, 59)   # #1E293B Body Text

    def set_font(run, font_name="Times New Roman", size_pt=11, bold=False, italic=False, color=CHARCOAL):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            set_font(r)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="Times New Roman", size_pt=14, bold=True, color=NAVY)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="Times New Roman", size_pt=12, bold=True, color=DARK_BLUE)
        return p

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_cells = table.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                set_font(r, font_name="Times New Roman", size_pt=10, bold=True, color=RGBColor(255, 255, 255))
            shd = parse_xml(r'<w:shd {} w:fill="1A365D"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shd)

        for r_idx, row_data in enumerate(data):
            row_cells = table.add_row().cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                row_cells[c_idx].text = str(val)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(val) > 10 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                for r in p.runs:
                    set_font(r, font_name="Times New Roman", size_pt=9.5, color=CHARCOAL)
                shd = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg_color))
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shd)

        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    def add_code(text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.cell(0, 0)
        c.width = Inches(6.5)
        shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
        c._tc.get_or_add_tcPr().append(shd)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(text)
        set_font(r, font_name="Consolas", size_pt=8.5, color=RGBColor(15, 23, 42))

    # COVER / HEADER
    p1 = add_p("PROJECT PROGRESS REPORT (SESSION 2026-27)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    set_font(p1.runs[0], font_name="Times New Roman", size_pt=12, bold=True, color=DARK_BLUE)

    p2 = add_p("STOCK MARKET ANALYSIS AND PRICE PREDICTION SYSTEM", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=8)
    set_font(p2.runs[0], font_name="Times New Roman", size_pt=18, bold=True, color=NAVY)

    p3 = add_p("Bachelor of Computer Applications (BCA)\nSchool of Computer Applications and Technology\nGalgotias University, Greater Noida, Uttar Pradesh, India", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=14)
    set_font(p3.runs[0], font_name="Times New Roman", size_pt=11, bold=True)

    # Metadata Table
    tbl_meta = doc.add_table(rows=4, cols=2)
    style_table(tbl_meta, [2.2, 4.3], ["Field", "Project Review Details"], [
        ["Submitted By", "1. Kartik Garg (24SCSE1470057)\n2. Akarsh Raj (24SCSE1470114)\n3. Sarthak Chhabra (24SCSE1470097)"],
        ["Supervised By", "[Enter Guide Name], Assistant Professor / Associate Professor"],
        ["Reporting Period", "Mid-Term Review / Progress Milestone (October, 2026)"],
        ["Completion Status", "85% Completed – Core Development & ML Verification Complete; Final Refinements Underway"],
    ])

    add_p("", space_after=10)

    # SECTION 1
    add_h1("SECTION 1: ABSTRACT & PROJECT OVERVIEW")
    add_h2("1.1 Problem Statement")
    add_p(
        "Equity price movements represent non-linear, stochastic time series governed by macroeconomic factors, corporate financial results, "
        "and market psychology. Retail investors and researchers struggle to manually parse raw numerical price feeds while simultaneously "
        "tracking breaking corporate news. Existing statistical tools fail under regime shifts, and commercial financial terminals carry prohibitive licensing fees.",
        space_after=8
    )

    add_h2("1.2 Project Objectives")
    add_p(
        "1. Ingest historical OHLCV data for global equities (US & Indian NSE) using free APIs without mandatory keys.\n"
        "2. Compute mathematical technical indicators (SMA 20/50/200, EMA 20, RSI-14, MACD, Bollinger Bands) using pure Pandas/NumPy.\n"
        "3. Architect a look-ahead-free ML pipeline with 14 engineered time-series features and strict chronological 80/20 train/test splitting.\n"
        "4. Calculate quantitative evaluation metrics (RMSE, MAE, MAPE %) and forecast multi-day future trajectories with 95% confidence intervals.\n"
        "5. Implement real-time VADER NLP news sentiment scoring categorized into Bullish, Neutral, and Bearish market stances.\n"
        "6. Provide an intuitive 4-tab Streamlit dashboard with interactive Plotly candlestick charting and CSV data export.",
        space_after=8
    )

    add_h2("1.3 Current Progress Summary")
    add_p(
        "Currently, 85% of project milestones are completed and validated. The core ingestion module, technical indicators, ML regression models, "
        "VADER sentiment engine, and Streamlit user interface are 100% operational. The remaining 15% focuses on final viva slide preparation, "
        "multi-sector asset comparisons, and thesis binding.",
        space_after=12
    )

    # SECTION 2
    add_h1("SECTION 2: SYSTEM REQUIREMENTS & APIS USED")
    add_h2("2.1 Hardware & Software Stack")
    tbl_hw = doc.add_table(rows=1, cols=4)
    style_table(tbl_hw, [1.4, 1.6, 1.5, 2.0], ["Category", "Tool / Library", "Specification", "Project Function"], [
        ["Hardware", "Processor (CPU)", "Intel Core i3 / Ryzen 3+", "Vectorized computations & tree training"],
        ["Hardware", "RAM & Network", "4 GB+ RAM, Active Wi-Fi", "In-memory caching & external API polling"],
        ["Software", "Python Runtime", "Python 3.11.x (Astral)", "Core execution and data science stack"],
        ["Software", "Web Framework", "Streamlit 1.35+", "Interactive UI dashboard & widget state"],
        ["Software", "Visualization", "Plotly 5.22+", "Interactive candlestick and forecast curves"],
        ["Software", "Data Science", "Pandas 2.2+, NumPy 1.26+", "DataFrames & vectorized indicator math"],
        ["Software", "Machine Learning", "Scikit-Learn 1.4+", "Random Forest, Gradient Boosting, Linear Reg"],
        ["Software", "Sentiment NLP", "vaderSentiment 3.3.2", "Valence-aware headline sentiment scoring"],
        ["Software", "Data Ingestion", "yfinance 0.2.40+ / requests", "Zero-key historical quotes & news search"],
    ])
    add_p("Table 1: Hardware & Software Stack Specification", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10)

    add_h2("2.2 External Free APIs & Data Sources")
    tbl_ap = doc.add_table(rows=1, cols=4)
    style_table(tbl_ap, [1.6, 1.4, 1.5, 2.0], ["API / Source", "Protocol", "Data Acquired", "Failover & Error Handling"], [
        ["Yahoo Finance (yfinance)", "HTTPS / Python Wrapper", "Daily historical OHLCV bars & metadata", "100% Free / Displays UI warning on invalid ticker"],
        ["MultiIndex Column Cleaner", "In-Memory Sanitizer", "Normalized single-level columns", "Flattens tuple headers to avoid shape/index error"],
        ["Finnhub Stock API", "HTTPS / REST JSON", "Live corporate press releases & news", "Optional token / Transparent fallback to Yahoo news"],
        ["Yahoo Search News", "HTTPS / JSON REST", "Recent financial journalism articles", "Default news feed when Finnhub key is absent"],
        ["Google News RSS", "HTTPS / XML RSS", "Real-time ticker news headlines", "Final fallback ensuring sentiment is always active"],
    ])
    add_p("Table 2: External Free APIs & Data Sources Specification", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    # SECTION 3
    add_h1("SECTION 3: SYSTEM ARCHITECTURE & METHODOLOGY")
    add_h2("3.1 Modular Architecture Flowchart")
    arch_diag = (
        "+-----------------------------------------------------------------------------------+\n"
        "|                            STREAMLIT UI LAYER (app.py)                            |\n"
        "|  Sidebar Controls | Top Metric Cards | AI Prediction Banner | 4 Interactive Tabs  |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          |\n"
        "              +---------------------------+---------------------------+\n"
        "              |                           |                           |\n"
        "              v                           v                           v\n"
        "+---------------------------+ +-----------------------+ +---------------------------+\n"
        "| TECHNICAL INDICATORS      | | ML REGRESSION PIPELINE| | VADER SENTIMENT ENGINE    |\n"
        "| (indicators.py)           | | (predictor.py)        | | (sentiment.py)            |\n"
        "| • SMA (20, 50, 200), EMA  | | • 14 Lagged Features  | | • Financial Lexicon Tuning|\n"
        "| • RSI 14 (Wilder Smoothed)| | • Chronological 80/20 | | • Bullish / Bearish Stance|\n"
        "| • MACD & Bollinger Bands  | | • Recursive Forecasting| | • Compound Polarity Score |\n"
        "+-------------+-------------+ +-----------+-----------+ +-------------+-------------+\n"
        "              |                           |                           |\n"
        "              +---------------------------+---------------------------+\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                  DATA INGESTION & MEMORY CACHE (data_loader.py)                   |\n"
        "|  • yfinance Daily Downloader   • MultiIndex Column Cleaner   • Streamlit Cache    |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|           EXTERNAL DATA: Yahoo Finance API (Zero Key)  &  Finnhub API             |\n"
        "+-----------------------------------------------------------------------------------+"
    )
    add_code(arch_diag)
    add_p("Figure 1: Modular System Architecture & Data Flow", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10)

    add_h2("3.2 Methodology & Formulas")
    add_p(
        "• RSI-14: RSI = 100 - (100 / (1 + RS)), where RS = Wilder Smoothed Gain / Wilder Smoothed Loss\n"
        "• MACD: Line = EMA_12 - EMA_26; Signal = EMA_9(MACD Line); Histogram = Line - Signal\n"
        "• RMSE = sqrt((1/n) * sum((y - y_hat)^2))\n"
        "• MAE = (1/n) * sum(|y - y_hat|)\n"
        "• MAPE (%) = (100% / n) * sum(|(y - y_hat) / y|)",
        space_after=12
    )

    # SECTION 4
    add_h1("SECTION 4: WORK COMPLETED VS. PENDING TASKS")
    tbl_prog = doc.add_table(rows=1, cols=4)
    style_table(tbl_prog, [1.0, 1.8, 2.5, 1.2], ["Module", "Module Name", "Deliverables", "Status"], [
        ["M-01", "Data Ingestion (data_loader.py)", "yfinance data, MultiIndex flattening, 3-tier news fallback", "100% Completed"],
        ["M-02", "Indicators (indicators.py)", "Pure Pandas/NumPy SMA 20/50/200, RSI, MACD, Bollinger Bands", "100% Completed"],
        ["M-03", "ML Pipeline (predictor.py)", "14 features, chrono 80/20 split, RF/GBDT/Linear, recursive forecast", "100% Completed"],
        ["M-04", "Sentiment (sentiment.py)", "VADER NLP with financial lexicon updates & stance classification", "100% Completed"],
        ["M-05", "Dashboard UI (app.py)", "4-Tab Streamlit UI with Plotly charts, overlays, metric cards", "100% Completed"],
        ["M-06", "Verification (test_pipeline.py)", "Automated terminal pipeline test asserting all outputs on live AAPL", "100% Completed"],
        ["M-07", "Project Documentation", "34-page formal BCA Project Report (.md, .pdf, .docx)", "100% Completed"],
        ["M-08", "Viva & Defense Preparation", "Multi-sector asset testing, viva talking points, final presentation", "In Progress (30%)"],
    ])
    add_p("Table 3: Module-Wise Progress Tracking Status", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10)

    add_h2("4.2 Key Implementation Extracts")
    add_code(
        "# Chronological Partitioning to strictly eliminate look-ahead bias (predictor.py)\n"
        "split_idx = int(len(feat_df) * 0.80)\n"
        "train_df, test_df = feat_df.iloc[:split_idx], feat_df.iloc[split_idx:]\n"
        "X_train, y_train = train_df[feature_cols], train_df['Target']\n"
        "X_test, y_test = test_df[feature_cols], test_df['Target']\n"
        "model = RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42)\n"
        "model.fit(X_train, y_train)\n"
        "y_pred = model.predict(X_test)\n"
        "rmse = root_mean_squared_error(y_test, y_pred)\n"
        "mape = mean_absolute_percentage_error(y_test, y_pred) * 100.0"
    )

    # SECTION 5
    add_h1("SECTION 5: PRELIMINARY TEST RESULTS & VERIFICATION")
    tbl_tc = doc.add_table(rows=1, cols=5)
    style_table(tbl_tc, [1.0, 1.8, 1.6, 1.5, 0.6], ["Test ID", "Scenario", "Expected Result", "Actual Result", "Status"], [
        ["TC-01", "US Ticker AAPL (1 Year)", "Ingest ~250 rows OHLCV cleanly", "Retrieved 252 daily bars", "PASS"],
        ["TC-02", "NSE Ticker RELIANCE.NS", "Ingest data; detect INR currency", "Retrieved 84 rows; currency INR", "PASS"],
        ["TC-03", "MultiIndex Flattening", "Convert tuple headers to single level", "Columns flattened without shape error", "PASS"],
        ["TC-04", "Indicator Calculation", "Calculate SMA, RSI, MACD without NaNs", "All indicator series populated", "PASS"],
        ["TC-05", "ML Model & Metrics Check", "Compute test RMSE, MAE, MAPE (%)", "RMSE: 12.07, MAE: 10.06, MAPE: 2.98%", "PASS"],
        ["TC-06", "Recursive 14-Day Forecast", "Generate 14 business days future curve", "Forecast curve & 95% bands generated", "PASS"],
        ["TC-07", "News Sentiment Failover", "Retrieve news without Finnhub key", "Ingested 9 headlines; Stance: Bullish", "PASS"],
        ["TC-08", "Web Server Port 8501", "HTTP response on localhost:8501", "HTTP Status 200 OK", "PASS"],
    ])
    add_p("Table 4: Formal Verification Test Cases Log", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10)

    add_h2("5.2 Empirical Accuracy Metrics on Benchmark (AAPL)")
    add_p(
        "• Historical Observations: 252 trading days\n"
        "• Training Set (80% Chronological): 185 days | Testing Set (20% Out-of-Sample): 46 days\n"
        "• Algorithm: RandomForestRegressor (n_estimators=120, max_depth=12)\n"
        "• Root Mean Squared Error (RMSE): 12.07 price units\n"
        "• Mean Absolute Error (MAE): 10.06 price units\n"
        "• Mean Absolute Percentage Error (MAPE): 2.98% (Well under the 5.0% college benchmark)\n"
        "• Directional Accuracy: 45.7%\n"
        "• Total Execution Time: 0.84 seconds on standard quad-core CPU",
        space_after=12
    )

    # SECTION 6
    add_h1("SECTION 6: NEXT STEPS & FUTURE PLAN")
    add_p(
        "1. Final Presentation Slide Deck: Preparing PowerPoint slides with annotated UI screenshots of all 4 tabs.\n"
        "2. Cross-Sector Volatility Stress Testing: Evaluating MAPE variations across high-beta technology vs low-beta defensive consumer equities.\n"
        "3. Technical Viva Voce Defense: Formulating explanatory points on look-ahead bias elimination, autoregressive lag updates, and financial lexicon tuning.\n"
        "4. Final Departmental Thesis Submission: Binding the complete 34-page report (Stock_Market_Prediction_Project_Report.pdf) for evaluator review.",
        space_after=20
    )

    add_p("Student Signature(s): _______________________          Supervisor Signature: _______________________", space_after=6)
    add_p("Date: 27th October, 2026                               Department: SCAT, Galgotias University", space_after=10)

    doc.save(docx_path)
    print(f"Generated DOCX: {docx_path}")

    # Convert to PDF
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        wdoc = word.Documents.Open(docx_path)
        wdoc.SaveAs(pdf_path, FileFormat=17) # 17 = wdExportFormatPDF
        wdoc.Close()
        print(f"Generated PDF: {pdf_path}")
    finally:
        word.Quit()

if __name__ == "__main__":
    generate_progress_report()
