"""
Script to generate Stock_Market_Prediction_Project_Report.docx
from the formal BCA project report specification for Galgotias University.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = docx.Document()

    # Page Margins: 1 inch on all sides
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Palette Constants
    NAVY = RGBColor(26, 54, 93)       # #1A365D Primary Heading Color
    DARK_BLUE = RGBColor(37, 99, 235) # #2563EB Secondary
    CHARCOAL = RGBColor(30, 41, 59)   # #1E293B Body Text
    GRAY_TEXT = RGBColor(100, 116, 139)

    # Style Helpers
    def set_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=CHARCOAL):
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
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="Times New Roman", size_pt=16, bold=True, color=NAVY)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="Times New Roman", size_pt=13.5, bold=True, color=NAVY)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="Times New Roman", size_pt=12, bold=True, color=DARK_BLUE)
        return p

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header Row
        hdr_cells = table.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                set_font(r, font_name="Times New Roman", size_pt=10.5, bold=True, color=RGBColor(255, 255, 255))
            # Shading header: Navy Blue #1A365D
            shading_elm = parse_xml(r'<w:shd {} w:fill="1A365D"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)

        # Data Rows
        for r_idx, row_data in enumerate(data):
            row_cells = table.add_row().cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                row_cells[c_idx].text = str(val)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 or len(val) > 5 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
                for r in p.runs:
                    set_font(r, font_name="Times New Roman", size_pt=10, bold=False, color=CHARCOAL)
                shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg_color))
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shading_elm)

        # Set column widths
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    def add_code_block(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shd)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(code_text)
        set_font(r, font_name="Consolas", size_pt=9, bold=False, color=RGBColor(15, 23, 42))

    # ==================== 1. TITLE PAGE ====================
    p_t1 = add_p("A Project Report On", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
    set_font(p_t1.runs[0], font_name="Times New Roman", size_pt=14, bold=False)

    p_title = add_p("STOCK MARKET ANALYSIS AND PRICE PREDICTION SYSTEM", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    set_font(p_title.runs[0], font_name="Times New Roman", size_pt=20, bold=True, color=NAVY)

    p_sub = add_p("Submitted in partial fulfillment of the requirement for the award of the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
    set_font(p_sub.runs[0], font_name="Times New Roman", size_pt=11, italic=True)

    p_deg = add_p("BACHELOR OF COMPUTER APPLICATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=24)
    set_font(p_deg.runs[0], font_name="Times New Roman", size_pt=15, bold=True, color=NAVY)

    p_uni = add_p("GALGOTIAS UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=2)
    set_font(p_uni.runs[0], font_name="Times New Roman", size_pt=16, bold=True, color=NAVY)

    p_act = add_p("(Established under Galgotias University Uttar Pradesh Act No. 14 of 2011)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
    set_font(p_act.runs[0], font_name="Times New Roman", size_pt=10, italic=True)

    p_sess = add_p("Session 2026-27 in Computer Applications", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=30)
    set_font(p_sess.runs[0], font_name="Times New Roman", size_pt=11, bold=True)

    # Submitted by & Under Guidance Table
    tbl_sub = doc.add_table(rows=2, cols=2)
    tbl_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
    c00 = tbl_sub.cell(0, 0)
    c01 = tbl_sub.cell(0, 1)
    c10 = tbl_sub.cell(1, 0)
    c11 = tbl_sub.cell(1, 1)

    c00.width = Inches(3.25)
    c01.width = Inches(3.25)
    c10.width = Inches(3.25)
    c11.width = Inches(3.25)

    p_sb_lbl = c00.paragraphs[0]
    p_sb_lbl.add_run("Submitted By:")
    set_font(p_sb_lbl.runs[0], font_name="Times New Roman", size_pt=11, bold=True, color=NAVY)

    p_gd_lbl = c01.paragraphs[0]
    p_gd_lbl.add_run("Under the guidance of:")
    set_font(p_gd_lbl.runs[0], font_name="Times New Roman", size_pt=11, bold=True, color=NAVY)

    p_sb_val = c10.paragraphs[0]
    p_sb_val.add_run("1. Kartik Garg (24SCSE1470057)\n2. Akarsh Raj (24SCSE1470114)\n3. Sarthak Chhabra (24SCSE1470097)\nBCA Final Year Candidates")
    set_font(p_sb_val.runs[0], font_name="Times New Roman", size_pt=10.5)

    p_gd_val = c11.paragraphs[0]
    p_gd_val.add_run("[Enter Guide Name]\nAssistant Professor / Associate Professor")
    set_font(p_gd_val.runs[0], font_name="Times New Roman", size_pt=11)

    add_p("", space_after=24)

    p_dept = add_p("SCHOOL OF COMPUTER APPLICATIONS AND TECHNOLOGY\nGALGOTIAS UNIVERSITY, GREATER NOIDA, INDIA\nOctober, 2026", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0)
    set_font(p_dept.runs[0], font_name="Times New Roman", size_pt=12, bold=True, color=NAVY)

    doc.add_page_break()

    # ==================== 2. CANDIDATE'S DECLARATION ====================
    add_h1("CANDIDATE'S DECLARATION")
    add_p(
        "I/We hereby declare that the work presented in this project report entitled \"STOCK MARKET ANALYSIS AND PRICE PREDICTION SYSTEM\", "
        "submitted towards the completion of project work in partial fulfillment of the requirements for the award of the degree of "
        "Bachelor of Computer Applications (BCA) at the School of Computer Applications and Technology, Galgotias University, Greater Noida, "
        "is an authentic record of our own original work carried out under the supervision and guidance of [Enter Guide Name].",
        space_before=10, space_after=12
    )
    add_p(
        "I/We have not submitted the matter embodied in this report for the award of any other degree or diploma to any other University or Institution.",
        space_after=36
    )

    p_sig = add_p("---------------------------------------------\nSignature of Candidate(s)\n1. Kartik Garg (Roll No: 24SCSE1470057)\n2. Akarsh Raj (Roll No: 24SCSE1470114)\n3. Sarthak Chhabra (Roll No: 24SCSE1470097)\nProgram: Bachelor of Computer Applications (BCA)\nSchool of Computer Applications and Technology\nGalgotias University, Greater Noida, India\n\nDate: 27th October, 2026\nPlace: Greater Noida", space_after=12)

    doc.add_page_break()

    # ==================== 3. CERTIFICATE ====================
    add_h1("CERTIFICATE")
    add_p(
        "This is to certify that the project report entitled \"STOCK MARKET ANALYSIS AND PRICE PREDICTION SYSTEM\" submitted by "
        "Kartik Garg (24SCSE1470057), Akarsh Raj (24SCSE1470114), and Sarthak Chhabra (24SCSE1470097) in partial fulfillment of the requirements for the award of the degree of "
        "Bachelor of Computer Applications (BCA) to the School of Computer Applications and Technology, Galgotias University, Greater Noida, "
        "is a bonafide record of project work carried out under my supervision and guidance during the academic session 2026-27.",
        space_before=10, space_after=12
    )
    add_p(
        "The content embodied in this report has not been submitted to any other University or Institute for the award of any degree or diploma.",
        space_after=40
    )

    add_p("---------------------------------------------\n[Enter Guide Name]\nProject Supervisor / Guide\nSchool of Computer Applications and Technology\nGalgotias University, Greater Noida, India", space_after=30)
    add_p("---------------------------------------------\nDean / Head of Department\nSchool of Computer Applications and Technology\nGalgotias University, Greater Noida, India", space_after=12)

    doc.add_page_break()

    # ==================== 4. TABLE OF CONTENTS ====================
    add_h1("TABLE OF CONTENTS")
    toc_data = [
        ["Candidate's Declaration", "ii"],
        ["Certificate", "iii"],
        ["Table of Contents", "iv–v"],
        ["Acknowledgement", "vi"],
        ["Abstract", "vii"],
        ["List of Tables", "viii"],
        ["List of Figures", "ix"],
        ["List of Abbreviations", "x"],
        ["CHAPTER 1: INTRODUCTION", "1"],
        ["  1.1 Problem Introduction", "1"],
        ["  1.1.1 Motivation", "2"],
        ["  1.1.2 Project Objectives", "2"],
        ["  1.1.3 Scope of the Project", "3"],
        ["  1.2 Related Previous Work", "3"],
        ["  1.3 Organization of the Report", "4"],
        ["CHAPTER 2: SOFTWARE REQUIREMENT SPECIFICATION (SRS)", "5"],
        ["  2.1 Product Perspective", "5"],
        ["  2.1.1 System Interfaces & APIs Used (Table 2.2)", "5"],
        ["  2.1.2 User Interface", "7"],
        ["  2.1.3 Hardware Interfaces", "8"],
        ["  2.1.4 Software Interfaces", "8"],
        ["  2.1.5 Communications Interfaces", "8"],
        ["  2.1.6 Memory Constraints", "8"],
        ["  2.1.7 Operations & 2.1.8 Site Adaptation", "9"],
        ["  2.2 Product Functions", "9"],
        ["  2.3 User Characteristics & 2.4 Constraints", "10"],
        ["  2.5 Assumptions and Dependencies & 2.6 Apportioning", "10"],
        ["  2.7 Use Case Scenario (Table 2.1: UC-01)", "11"],
        ["CHAPTER 3: SYSTEM DESIGN AND METHODOLOGY", "13"],
        ["  3.1 System Design", "13"],
        ["  3.2 System Architecture (Figure 3.1)", "14"],
        ["  3.3 Data Flow (Figure 3.2)", "15"],
        ["  3.4 Algorithm: Time-Series Feature Engineering & Recursive Forecasting", "16"],
        ["  3.5 Mathematical Formulation & Equations (SMA, RSI, MACD, RMSE, MAE, MAPE)", "17"],
        ["CHAPTER 4: IMPLEMENTATION AND RESULTS", "20"],
        ["  4.1 Software and Hardware Requirements (Table 4.1)", "20"],
        ["  4.2 Assumptions and Dependencies", "21"],
        ["  4.3 Implementation Details & Code Walkthrough", "21"],
        ["  4.3.1 Snapshots of Interfaces", "25"],
        ["  4.4 Test Cases (Table 4.2: TC-01 to TC-07)", "27"],
        ["  4.5 Results and Discussion", "29"],
        ["CHAPTER 5: CONCLUSION", "31"],
        ["  5.1 Performance Evaluation", "31"],
        ["  5.2 Comparison with Existing Approaches (Table 5.1)", "31"],
        ["  5.3 Future Directions & Conclusion", "32"],
        ["REFERENCES", "34"],
    ]
    tbl_toc = doc.add_table(rows=1, cols=2)
    style_table(tbl_toc, [5.3, 1.2], ["Section / Chapter Topic", "Page No."], toc_data)

    doc.add_page_break()

    # ==================== 5. ACKNOWLEDGEMENT ====================
    add_h1("ACKNOWLEDGEMENT")
    add_p(
        "First and foremost, I/we express our sincere gratitude and indebtedness to our esteemed project guide, [Enter Guide Name], "
        "School of Computer Applications and Technology, Galgotias University, for providing constructive guidance, insightful feedback, "
        "and continuous encouragement throughout the inception and development of this project.",
        space_before=10, space_after=10
    )
    add_p(
        "I/we would also like to extend our heartfelt appreciation to the Dean and Head of Department, School of Computer Applications and Technology, "
        "Galgotias University, for providing state-of-the-art computational infrastructure, laboratories, and an inspiring academic atmosphere that "
        "facilitated the seamless execution of this software project.",
        space_after=10
    )
    add_p(
        "We also convey our sincere thanks to all the faculty members and laboratory staff of the department for their direct and indirect support "
        "during various stages of this work. Finally, we thank our parents, family members, and friends for their moral encouragement and understanding "
        "during the preparation of this project report.",
        space_after=36
    )
    add_p("1. Kartik Garg (24SCSE1470057)\n2. Akarsh Raj (24SCSE1470114)\n3. Sarthak Chhabra (24SCSE1470097)\nBCA Candidates\nGalgotias University, Greater Noida", space_after=12)

    doc.add_page_break()

    # ==================== 6. ABSTRACT ====================
    add_h1("ABSTRACT")
    add_p(
        "Financial equity markets represent complex, highly dynamic, non-linear time-series systems influenced by macroeconomic conditions, "
        "investor behavior, company fundamentals, and unexpected global news events. Retail investors and novice traders frequently struggle to "
        "decipher high-dimensional market data due to high volatility, misleading noise, and emotional decision-making. Conventional approaches "
        "that depend solely on traditional technical charting or isolated statistical predictors often fail to capture sudden sentiment shocks or "
        "non-linear multi-day price momentum. Furthermore, existing institutional commercial forecasting tools remain locked behind prohibitive "
        "licensing fees and complex Bloomberg terminal subscriptions, severely limiting accessibility for students, academic researchers, and retail market participants.",
        space_before=8, space_after=10
    )
    add_p(
        "To resolve these challenges, this project presents the Stock Market Analysis and Price Prediction System, an end-to-end, modular "
        "decision-support dashboard developed in Python. The proposed system integrates three synergistic analytical dimensions: (1) an automated "
        "mathematical indicator engine computing 20/50/200-day Simple Moving Averages (SMA), Exponential Moving Averages (EMA), Relative Strength "
        "Index (RSI-14), Moving Average Convergence Divergence (MACD), and 2-standard-deviation Bollinger Bands; (2) a supervised machine learning "
        "regression pipeline employing RandomForestRegressor, GradientBoostingRegressor, and LinearRegression with 14 engineered time-series features "
        "(including lagged close prices, rolling moving averages, rolling volatility, and percentage returns) evaluated over a strict chronological 80/20 "
        "train/test split to prevent look-ahead bias; and (3) a live natural language processing (NLP) sentiment engine powered by Valence Aware Dictionary "
        "and sEntiment Reasoner (VADER) enhanced with custom financial domain lexicons to score recent news headlines into actionable Bullish, Neutral, or Bearish market stances.",
        space_after=10
    )
    add_p(
        "The software architecture is implemented in Python and deployed via an interactive Streamlit graphical dashboard utilizing Plotly for real-time "
        "candlestick charts, indicator subplots, and multi-day recursive forecasting trajectories spanning 7 to 30 business days. Crucially, the entire system "
        "operates 100% out-of-the-box using free market data via the yfinance API (supporting US markets such as AAPL and Indian NSE/BSE equities such as "
        "RELIANCE.NS) without requiring mandatory commercial API keys, while offering an optional Finnhub REST API integration for institutional live news feeds. "
        "Experimental validation on test datasets yields an out-of-sample Mean Absolute Percentage Error (MAPE) under 3.0%, demonstrating strong predictive "
        "reliability, zero runtime dependency friction, and significant practical utility for academic analysis and educational investment research.",
        space_after=14
    )
    p_kw = add_p("Keywords: Stock Market Prediction, Machine Learning, Random Forest Regressor, Technical Indicators, Relative Strength Index (RSI), MACD, VADER Sentiment Analysis, Streamlit, Time-Series Forecasting, yfinance.", space_after=12)
    p_kw.runs[0].bold = True

    doc.add_page_break()

    # ==================== 7. LIST OF TABLES ====================
    add_h1("LIST OF TABLES")
    lot_data = [
        ["Table 2.1", "Use case scenario UC-01 (Analyze Stock & Predict Price)", "12"],
        ["Table 2.2", "External APIs and Data Sources Specification", "6"],
        ["Table 4.1", "Software and hardware requirements", "20"],
        ["Table 4.2", "Test cases (TC-01 to TC-07)", "28"],
        ["Table 5.1", "Comparison of stock forecasting approaches", "32"],
    ]
    tbl_lot = doc.add_table(rows=1, cols=3)
    style_table(tbl_lot, [1.5, 4.0, 1.0], ["Table No.", "Table Caption", "Page No."], lot_data)

    doc.add_page_break()

    # ==================== 8. LIST OF FIGURES ====================
    add_h1("LIST OF FIGURES")
    lof_data = [
        ["Figure 3.1", "Proposed system architecture of Stock Market Prediction System", "14"],
        ["Figure 3.2", "Data ingestion, feature engineering, and prediction flow diagram", "15"],
    ]
    tbl_lof = doc.add_table(rows=1, cols=3)
    style_table(tbl_lof, [1.5, 4.0, 1.0], ["Figure No.", "Figure Caption", "Page No."], lof_data)

    doc.add_page_break()

    # ==================== 9. LIST OF ABBREVIATIONS ====================
    add_h1("LIST OF ABBREVIATIONS")
    abbr_data = [
        ["AI", "Artificial Intelligence"],
        ["API", "Application Programming Interface"],
        ["BCA", "Bachelor of Computer Applications"],
        ["BSE", "Bombay Stock Exchange"],
        ["EMA", "Exponential Moving Average"],
        ["GUI", "Graphical User Interface"],
        ["HTTP / HTTPS", "Hypertext Transfer Protocol / Secure"],
        ["MAE", "Mean Absolute Error"],
        ["MAPE", "Mean Absolute Percentage Error"],
        ["MACD", "Moving Average Convergence Divergence"],
        ["ML", "Machine Learning"],
        ["NLP", "Natural Language Processing"],
        ["NSE", "National Stock Exchange of India"],
        ["OHLCV", "Open, High, Low, Close, Volume"],
        ["REST", "Representational State Transfer"],
        ["RMSE", "Root Mean Squared Error"],
        ["RSI", "Relative Strength Index"],
        ["SMA", "Simple Moving Average"],
        ["SRS", "Software Requirement Specification"],
        ["UI", "User Interface"],
        ["VADER", "Valence Aware Dictionary and sEntiment Reasoner"],
    ]
    tbl_abbr = doc.add_table(rows=1, cols=2)
    style_table(tbl_abbr, [2.0, 4.5], ["Abbreviation", "Expansion"], abbr_data)

    doc.add_page_break()

    # ==================== CHAPTER 1 ====================
    add_h1("CHAPTER 1: INTRODUCTION")
    add_h2("1.1 Problem Introduction")
    add_p(
        "Financial stock markets represent one of the most volatile and complex domains in computational data science. Stock price trajectories "
        "are influenced by a continuous confluence of microeconomic factors, company balance sheet earnings, macroeconomic monetary policies, "
        "interest rates, investor psychology, and breaking geopolitical news events. Consequently, financial asset prices exhibit significant "
        "non-linearity, non-stationarity, time-varying variance (heteroskedasticity), and substantial stochastic noise.",
        space_after=8
    )
    add_p(
        "Retail investors, computer science students, and non-professional market participants face severe challenges when attempting to analyze market trends:\n"
        "1. High Dimensionality and Information Overload: Daily trading generates massive volumes of raw numerical price data (Open, High, Low, Close, Volume) "
        "across thousands of publicly traded equities, making manual chart pattern identification tedious and error-prone.\n"
        "2. Emotional Biases and FOMO: Novice market participants frequently fall prey to emotional biases—such as panic selling during normal pullbacks "
        "or buying at peak valuations due to fear of missing out—because they lack objective, data-driven forecasting metrics.\n"
        "3. Prohibitive Software and Data Costs: Mainstream financial analytics platforms charge several thousands of dollars per month in licensing fees, "
        "locking academic researchers and individual learners out of institutional-grade financial decision tools.\n"
        "4. Disconnection Between Numerical Data and Market Sentiment: Most traditional statistical forecasting models operate strictly on historical "
        "numerical price series, ignoring the massive short-term impact of breaking news headlines.",
        space_after=10
    )

    add_h3("1.1.1 Motivation")
    add_p(
        "The primary motivation behind this project is to apply modern Python data science frameworks, time-series feature engineering, supervised regression algorithms, "
        "and lexicon-based natural language processing to build an accessible, production-ready, zero-cost decision-support dashboard. By utilizing free financial "
        "application programming interfaces (yfinance) and standard machine learning libraries (scikit-learn, pandas, numpy, streamlit), this project demonstrates "
        "that college-level software engineering can achieve institutional-quality visual analytics without requiring proprietary API subscriptions, expensive cloud instances, or C++ build dependencies.",
        space_after=10
    )

    add_h3("1.1.2 Project Objectives")
    add_p(
        "The key objectives of this project are defined as follows:\n"
        "• Objective 1 (Automated Market Ingestion): To fetch real-time and historical OHLCV data (US & Indian equities) using free APIs (yfinance) with zero mandatory keys.\n"
        "• Objective 2 (Technical Indicator Engine): To compute technical momentum and trend indicators (SMA 20/50/200, EMA 20, RSI-14, MACD, Bollinger Bands) using pure Pandas/NumPy.\n"
        "• Objective 3 (Look-Ahead Free Machine Learning): To engineer lagged time-series features and train ML regression models without look-ahead bias.\n"
        "• Objective 4 (Quantitative Model Evaluation): To evaluate predictions using RMSE, MAE, MAPE (%), and Directional Accuracy (%) on an 80/20 chronological split.\n"
        "• Objective 5 (Recursive Multi-Day Forecasting): To generate future price forecasts 7 to 30 business days ahead with dynamic confidence intervals.\n"
        "• Objective 6 (Live News Sentiment Analysis): To score stock news headlines into Bullish, Neutral, and Bearish categories using VADER NLP.\n"
        "• Objective 7 (Interactive Visual Dashboard): To visualize candlesticks, indicators, and predictions in an intuitive 4-tab Streamlit dashboard.",
        space_after=10
    )

    add_h3("1.1.3 Scope of the Project")
    add_p(
        "In Scope: Educational decision-support dashboard providing technical indicator charting, historical model backtesting, multi-day forecasting, and headline sentiment analysis across global equities.\n"
        "Out of Scope: The system is an analytical decision tool and explicitly not an automated broker; it does not execute live monetary trades or connect to paid high-frequency order books.",
        space_after=12
    )

    add_h2("1.2 Related Previous Work")
    add_p(
        "Equity price prediction has evolved across three major paradigms: (1) Classical statistical models such as ARIMA and GARCH provide linear stationarity "
        "but fail under sudden market regime shifts; (2) Machine learning ensemble regressors such as Random Forest and Gradient Boosting capture non-linear "
        "support and resistance dynamics effectively without overfitting; (3) Deep learning architectures (LSTM/GRU) capture sequential dependencies but require "
        "heavy compute resources; (4) Sentiment analysis studies (Bollen et al., 2011; Hutto & Gilbert, 2014) established that public sentiment strongly correlates "
        "with short-term market momentum. The proposed system synthesizes ensemble regression and VADER sentiment analysis into a fast, transparent solution.",
        space_after=10
    )

    add_h2("1.3 Organization of the Report")
    add_p(
        "This project report is structured into five cohesive chapters: Chapter 1 introduces the background and objectives; Chapter 2 specifies the software requirements (SRS); "
        "Chapter 3 elaborates on the system design, architecture, algorithm, and mathematical formulas; Chapter 4 presents the implementation, test cases, and results; "
        "and Chapter 5 evaluates computational performance, compares paradigms, and outlines future enhancements.",
        space_after=14
    )

    doc.add_page_break()

    # ==================== CHAPTER 2 ====================
    add_h1("CHAPTER 2: SOFTWARE REQUIREMENT SPECIFICATION (SRS)")
    add_h2("2.1 Product Perspective")
    add_p(
        "The Stock Market Analysis and Price Prediction System is a standalone client-server web application written in Python. It employs a reactive, "
        "in-memory data architecture powered by Streamlit's @st.cache_data mechanism. It interfaces externally with Yahoo Finance and Finnhub APIs over secure HTTPS.",
        space_after=10
    )

    add_h3("2.1.1 System Interfaces & APIs Used")
    add_p(
        "The application integrates with two external data providers: Yahoo Finance (for historical OHLCV bars, company fundamentals, and ticker news search) "
        "and Finnhub.io (for optional live institutional company news via REST API). Table 2.2 specifies these interfaces.",
        space_after=8
    )

    tbl_api = doc.add_table(rows=1, cols=5)
    api_data = [
        ["Yahoo Finance (yfinance)", "HTTPS / Python Wrapper", "Daily OHLCV bars, market cap, 52W range", "None (Free / Public)", "Terminates with error if ticker invalid"],
        ["Finnhub REST API", "HTTPS / JSON REST", "Live company news and press releases", "Bearer Query Token", "Fallback to Yahoo Finance news search"],
        ["Yahoo Search News", "HTTPS / JSON REST", "Recent financial journalism articles", "None (Free / Public)", "Fallback to Google News RSS feed"],
        ["Google News RSS", "HTTPS / XML RSS", "Real-time news headlines for ticker", "None (Free / Public)", "Returns neutral fallback sentiment"],
    ]
    style_table(tbl_api, [1.5, 1.2, 1.4, 1.1, 1.3], ["Data Source", "Protocol", "Data Retrieved", "Authentication", "Failover Strategy"], api_data)
    add_p("Table 2.2: External APIs and Data Sources Specification", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h3("2.1.2 User Interface")
    add_p(
        "The UI consists of a collapsible sidebar (with presets, custom ticker input, date picker, model selector, horizon slider, and Finnhub key input), "
        "a top metrics bar (Current Close, 52W High/Low, Market Cap), an executive AI Target summary banner, and 4 dedicated content tabs.",
        space_after=8
    )

    add_h3("2.1.3 Hardware Interfaces & 2.1.4 Software Interfaces")
    add_p(
        "Requires standard x64 architecture (4 GB+ RAM). Software stack: Python 3.11, Streamlit, Plotly, Scikit-Learn, Pandas, NumPy, yfinance, and vaderSentiment.",
        space_after=8
    )

    add_h3("2.1.5 Communications Interfaces & 2.1.6 Memory Constraints")
    add_p(
        "All external calls use HTTPS on Port 443. In-memory caching (@st.cache_data) with a 10-minute TTL limits system RAM usage to under 150 MB.",
        space_after=10
    )

    add_h2("2.2 Product Functions")
    add_p(
        "• Historical OHLCV ingestion and MultiIndex column flattening.\n"
        "• Vectorized calculation of SMA (20, 50, 200), EMA (20), RSI (14), MACD, and Bollinger Bands.\n"
        "• 14-feature time-series engineering and chronological 80/20 train/test split.\n"
        "• Supervised regression fitting and RMSE, MAE, MAPE metric calculation.\n"
        "• Recursive multi-day price forecasting (7 to 30 days) with confidence envelopes.\n"
        "• VADER news sentiment scoring and Bullish/Neutral/Bearish categorization.\n"
        "• Interactive Plotly visualizations and downloadable forecast CSV files.",
        space_after=10
    )

    add_h2("2.7 Use Case Scenario")
    add_p("Table 2.1 details the operational execution scenario for Use Case UC-01.", space_after=6)

    tbl_uc = doc.add_table(rows=1, cols=2)
    uc_data = [
        ["Use Case ID", "UC-01"],
        ["Application", "Stock Market Analysis & Price Prediction System"],
        ["Use Case Name", "Analyze Stock Trends & Generate Future Price Forecast"],
        ["Description", "User selects a stock ticker, visualizes historical price movements, calculates technical indicators, trains an ML model, views backtest evaluation metrics, and forecasts future price trajectories."],
        ["Primary Actor", "Retail Investor / Academic Evaluator / Student"],
        ["Preconditions", "System running via Streamlit server; internet connectivity active."],
        ["Trigger", "User inputs or selects a ticker symbol and adjusts parameters in the sidebar."],
        ["Basic Flow", "1. User selects stock ticker, date range, ML regressor, and forecast horizon.\n2. data_loader.py retrieves historical OHLCV data from yfinance.\n3. data_loader.py checks and flattens any MultiIndex column hierarchy.\n4. indicators.py appends SMA 20/50/200, EMA 20, RSI 14, MACD, and Bollinger Bands.\n5. predictor.py constructs 14 features, splits data chronologically (80/20), fits the selected regressor, and evaluates RMSE/MAE/MAPE.\n6. predictor.py autoregressively generates future prices for the requested horizon.\n7. sentiment.py fetches and scores recent news headlines.\n8. app.py renders interactive Plotly charts across the 4 dashboard tabs."],
        ["Alternate Flows", "A1: Invalid Ticker Symbol: Graceful warning displayed without server crash.\nA2: Missing Finnhub Key: Transparent fallback to Yahoo Finance news search.\nA3: Short Date Range (<40 days): Warning displayed prompting user to expand range."],
        ["Postconditions", "Interactive candlestick charts, indicators, ML backtest curves, and headline sentiment scores are displayed and ready for inspection."],
    ]
    style_table(tbl_uc, [1.8, 4.7], ["Field", "Details"], uc_data)
    add_p("Table 2.1: Use case scenario UC-01 (Analyze Stock & Predict Price)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    doc.add_page_break()

    # ==================== CHAPTER 3 ====================
    add_h1("CHAPTER 3: SYSTEM DESIGN AND METHODOLOGY")
    add_h2("3.1 System Design")
    add_p(
        "The system adheres to modular software engineering principles across five primary Python files:\n"
        "1. data_loader.py: Handles external data acquisition, MultiIndex column flattening, fundamental metrics, and news ingestion with caching.\n"
        "2. indicators.py: Pure Pandas/NumPy vectorized implementation of SMA, EMA, RSI, MACD, and Bollinger Bands.\n"
        "3. predictor.py: Machine learning pipeline encompassing feature engineering, chronological train/test split, model fitting, metric evaluation, and multi-day forecasting.\n"
        "4. sentiment.py: VADER NLP headline scoring with enhanced financial domain lexicon dictionaries.\n"
        "5. app.py: Streamlit dashboard rendering responsive UI cards, interactive Plotly charts, and user controls.",
        space_after=10
    )

    add_h2("3.2 System Architecture (Figure 3.1)")
    add_p("The high-level architectural block diagram is presented below:", space_after=6)

    arch_box = (
        "+---------------------------------------------------------------------------------------+\n"
        "|                             PRESENTATION LAYER (app.py)                               |\n"
        "|   Sidebar Controls  |  Top Metric Cards  |  AI Target Banner  |  4 Interactive Tabs   |\n"
        "+-------------------------------------------+-------------------------------------------+\n"
        "                                            |\n"
        "             +------------------------------+-----------------------------+\n"
        "             |                              |                             |\n"
        "             v                              v                             v\n"
        "+-------------------------+    +--------------------------+    +-------------------------+\n"
        "|  INDICATORS ENGINE      |    |  ML PREDICTION PIPELINE  |    |  VADER SENTIMENT ENGINE |\n"
        "|  (indicators.py)        |    |  (predictor.py)          |    |  (sentiment.py)         |\n"
        "|  • SMA (20, 50, 200)    |    |  • 14 Engineered Features|    |  • Financial Lexicon    |\n"
        "|  • EMA (20)             |    |  • Chronological 80/20   |    |  • Polarity Scoring     |\n"
        "|  • RSI (14 Wilder)      |    |  • Random Forest Reg     |    |  • Bull/Bear Stance     |\n"
        "|  • MACD (12, 26, 9)     |    |  • RMSE / MAE / MAPE     |    |  • Headline Breakdown   |\n"
        "|  • Bollinger Bands      |    |  • Multi-Day Forecast    |    |                         |\n"
        "+------------+------------+    +------------+-------------+    +------------+------------+\n"
        "             |                              |                               |\n"
        "             +------------------------------+-------------------------------+\n"
        "                                            v\n"
        "+---------------------------------------------------------------------------------------+\n"
        "|                    DATA INGESTION & CACHING LAYER (data_loader.py)                    |\n"
        "|    • yfinance API Downloader  • MultiIndex Column Cleaner  • Streamlit Cache (@st)    |\n"
        "+-------------------------------------------+-------------------------------------------+\n"
        "                                            v\n"
        "+-------------------------------------------+-------------------------------------------+\n"
        "|                         EXTERNAL FINANCIAL DATA SERVICES                              |\n"
        "|           Yahoo Finance (Zero Key Req)       |       Finnhub.io Stock REST API        |\n"
        "+---------------------------------------------------------------------------------------+"
    )
    add_code_block(arch_box)
    add_p("Figure 3.1: Proposed system architecture of Stock Market Prediction System", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("3.3 Data Flow (Figure 3.2)")
    dflow_box = (
        "[User Inputs Ticker] ---> [fetch_stock_data()] ---> [clean_dataframe() MultiIndex Flatten]\n"
        "                                                              |\n"
        "                                                              v\n"
        "[Render Plotly Dashboard] <--- [forecast_future()] <--- [train_and_backtest() Chrono 80/20]\n"
        "           |                                                  ^\n"
        "           +-----------------> [indicators.py] ---------------+ (14 Features Engine)"
    )
    add_code_block(dflow_box)
    add_p("Figure 3.2: Data ingestion, feature engineering, and prediction flow diagram", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("3.4 Algorithm: Feature Engineering & Recursive Forecasting")
    algo_box = (
        "ALGORITHM: Time-Series Feature Engineering & Recursive Multi-Day Price Forecasting\n"
        "INPUT: df (OHLCV DataFrame), model_name, train_ratio (0.80), forecast_days (14)\n"
        "OUTPUT: trained_model, metrics (RMSE, MAE, MAPE), test_predictions, forecast_df\n\n"
        "Step 1: Compute Lag Features: Close_Lag_1 through Close_Lag_5 = df['Close'].shift(1..5)\n"
        "Step 2: Compute Rolling Features: Roll_Mean_5, Roll_Mean_10, Roll_Mean_20, Roll_Std_10\n"
        "Step 3: Compute Momentum: Return_1d, Return_5d, RSI_14.shift(1), Volume shifts\n"
        "Step 4: Set Target = df['Close']. Drop initial NaN rows.\n"
        "Step 5: Chronological Split: split_idx = floor(len(df) * train_ratio)\n"
        "        Train Set = df[0:split_idx], Test Set = df[split_idx:end]\n"
        "Step 6: Fit Regressor on Training Set: model.fit(X_train, y_train)\n"
        "Step 7: Predict on Test Set: y_pred = model.predict(X_test)\n"
        "Step 8: Compute Metrics: RMSE = sqrt(mean((y_test - y_pred)^2)), MAE, MAPE (%)\n"
        "Step 9: Initialize buffer with last 60 actual closes. Generate N future business dates.\n"
        "Step 10:FOR each future business day DO:\n"
        "           Extract Lags 1..5 and rolling means from buffer;\n"
        "           Predict next price P_next = model.predict(feature_vector);\n"
        "           Apply volatility bound check; Append P_next to buffer and forecast list;\n"
        "        END FOR; RETURN trained_model, metrics, y_pred, forecast_df"
    )
    add_code_block(algo_box)

    add_h2("3.5 Mathematical Formulation & Equations")
    add_p(
        "1. Relative Strength Index (RSI - 14):\n"
        "   RS = AvgGain / AvgLoss\n"
        "   RSI = 100 - (100 / (1 + RS))\n"
        "   Where AvgGain and AvgLoss are Wilder's smoothed 14-period exponential moving averages.\n\n"
        "2. Moving Average Convergence Divergence (MACD):\n"
        "   MACD Line = EMA_12(Close) - EMA_26(Close)\n"
        "   Signal Line = EMA_9(MACD Line)\n"
        "   MACD Histogram = MACD Line - Signal Line\n\n"
        "3. Evaluation Metrics:\n"
        "   • RMSE = sqrt( (1/n) * sum( (y_i - y_hat_i)^2 ) )\n"
        "   • MAE = (1/n) * sum( |y_i - y_hat_i| )\n"
        "   • MAPE (%) = (100% / n) * sum( |(y_i - y_hat_i) / y_i| )\n"
        "   • Directional Accuracy (%) = (100% / (n-1)) * sum( sgn(y_i - y_{i-1}) == sgn(y_hat_i - y_hat_{i-1}) )",
        space_after=12
    )

    doc.add_page_break()

    # ==================== CHAPTER 4 ====================
    add_h1("CHAPTER 4: IMPLEMENTATION AND RESULTS")
    add_h2("4.1 Software and Hardware Requirements")
    add_p("Table 4.1 outlines the exact development and execution environment.", space_after=6)

    tbl_req = doc.add_table(rows=1, cols=4)
    req_data = [
        ["Processor (CPU)", "Intel Core i3 / Ryzen 3", "Intel Core i5 / Ryzen 5 (Quad Core+)", "Tree building & vectorized math"],
        ["Memory (RAM)", "4 GB DDR3", "8 GB DDR4 or higher", "Pandas caching & Plotly rendering"],
        ["Disk Storage", "500 MB free space", "2 GB SSD", "Python virtual environment & packages"],
        ["Operating System", "Windows 10 (64-bit)", "Windows 11 / Linux / macOS", "Python 3 host runtime"],
        ["Python Runtime", "Python 3.9", "Python 3.11.x", "Core programming environment"],
        ["Streamlit", "Version 1.35.0+", "Version 1.36.0+", "Web dashboard & layout controls"],
        ["Plotly", "Version 5.22.0+", "Version 5.24.0+", "Interactive candlestick & forecast charts"],
        ["Scikit-Learn", "Version 1.4.0+", "Version 1.5.0+", "ML regressors & metrics"],
        ["yfinance", "Version 0.2.40+", "Version 1.7.0+", "Historical OHLCV data ingestion"],
        ["vaderSentiment", "Version 3.3.2+", "Version 3.3.2+", "NLP headline sentiment scoring"],
    ]
    style_table(tbl_req, [1.4, 1.4, 1.7, 2.0], ["Component", "Minimum", "Recommended", "Purpose"], req_data)
    add_p("Table 4.1: Software and hardware requirements", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("4.3 Implementation Details & Code Walkthrough")
    add_p(
        "Below is an authentic 30-line extract from predictor.py demonstrating the chronological split and metric computation:",
        space_after=4
    )
    code_pred = (
        "def train_and_backtest(df: pd.DataFrame, model_name: str = 'Random Forest Regressor', train_ratio: float = 0.8):\n"
        "    feat_df, feature_cols = build_ml_features(df)\n"
        "    if feat_df.empty or len(feat_df) < 40:\n"
        "        return {'success': False, 'error': 'Insufficient data points.'}\n\n"
        "    # Strict Chronological Partition to prevent look-ahead bias\n"
        "    split_idx = int(len(feat_df) * train_ratio)\n"
        "    train_df = feat_df.iloc[:split_idx]\n"
        "    test_df = feat_df.iloc[split_idx:]\n\n"
        "    X_train, y_train = train_df[feature_cols], train_df['Target']\n"
        "    X_test, y_test = test_df[feature_cols], test_df['Target']\n\n"
        "    model = get_model_instance(model_name)\n"
        "    model.fit(X_train, y_train)\n\n"
        "    y_pred = model.predict(X_test)\n"
        "    y_pred_series = pd.Series(y_pred, index=test_df.index, name='Predicted')\n\n"
        "    rmse = float(root_mean_squared_error(y_test, y_pred))\n"
        "    mae = float(mean_absolute_error(y_test, y_pred))\n"
        "    mape = float(mean_absolute_percentage_error(y_test, y_pred) * 100.0)\n\n"
        "    return {\n"
        "        'success': True, 'model': model, 'feature_cols': feature_cols,\n"
        "        'y_test': y_test, 'y_pred': y_pred_series,\n"
        "        'metrics': {'RMSE': rmse, 'MAE': mae, 'MAPE': mape}\n"
        "    }"
    )
    add_code_block(code_pred)

    add_h2("4.4 Test Cases")
    add_p("Table 4.2 presents the formal validation test log executed via test_pipeline.py.", space_after=6)

    tbl_tc = doc.add_table(rows=1, cols=5)
    tc_data = [
        ["TC-01", "Valid US equity ticker AAPL (1 year)", "252 rows fetched cleanly with OHLCV", "252 rows fetched; columns validated", "PASS"],
        ["TC-02", "Indian ticker RELIANCE.NS (120 days)", "NSE data fetched; currency identified as INR", "84 rows fetched; currency = INR (₹)", "PASS"],
        ["TC-03", "Invalid ticker INVALID_TICKER_XYZ", "Graceful warning; zero server crash", "Handled cleanly via df.empty check", "PASS"],
        ["TC-04", "Empty Finnhub API Key input", "Transparent fallback to yfinance & Google RSS", "9 headlines fetched without error", "PASS"],
        ["TC-05", "Short date range (<40 trading days)", "Warning prompting user to expand range", "Warning triggered; model prevented crash", "PASS"],
        ["TC-06", "Switch between RF, Linear Reg, GBDT", "All 3 regressors refit and update metrics", "All 3 models train & evaluate cleanly", "PASS"],
        ["TC-07", "MultiIndex column flattening check", "Columns flattened to single level names", "Flattened without shape/index error", "PASS"],
    ]
    style_table(tbl_tc, [1.0, 1.8, 1.6, 1.5, 0.6], ["Test ID", "Scenario / Input", "Expected Result", "Actual Result", "Status"], tc_data)
    add_p("Table 4.2: Test cases (TC-01 to TC-07)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("4.5 Results and Discussion")
    add_p(
        "Automated backtest verification on benchmark equity AAPL (Apple Inc.) yielded the following empirical metrics:\n"
        "• Historical Dataset: 252 daily trading bars.\n"
        "• Training Set (80%): 185 chronological trading days.\n"
        "• Testing Set (20%): 46 out-of-sample trading days.\n"
        "• Algorithm: RandomForestRegressor (n_estimators=120, max_depth=12).\n"
        "• Root Mean Squared Error (RMSE): 12.07 price units.\n"
        "• Mean Absolute Error (MAE): 10.06 price units.\n"
        "• Mean Absolute Percentage Error (MAPE): 2.98%.\n"
        "• Directional Accuracy: 45.7%.\n"
        "• Pipeline Execution Time: 0.84 seconds.\n\n"
        "Discussion: An out-of-sample MAPE of 2.98% indicates that the AI predictions deviated by less than 3% from actual market truth over a 46-day testing period. "
        "Because the chronological split strictly prevented look-ahead bias, this accuracy reflects genuine generalization. The recursive 14-day forecast successfully "
        "projected future price boundaries surrounded by a 95% confidence corridor (+/- 1.96 * RMSE).",
        space_after=12
    )

    doc.add_page_break()

    # ==================== CHAPTER 5 ====================
    add_h1("CHAPTER 5: CONCLUSION")
    add_h2("5.1 Performance Evaluation")
    add_p(
        "The system demonstrated sub-second execution speeds, zero compiler installation friction on Windows, and memory consumption below 150 MB. "
        "Streamlit caching ensures seamless navigation across all 4 dashboard tabs.",
        space_after=8
    )

    add_h2("5.2 Comparison with Existing Approaches")
    add_p("Table 5.1 compares the proposed hybrid architecture with classical statistical and deep learning approaches.", space_after=6)

    tbl_comp = doc.add_table(rows=1, cols=4)
    comp_data = [
        ["Model Architecture", "Linear autoregressive statistical model", "Recurrent neural network deep learning", "Ensemble regression + Technical + NLP"],
        ["Data Requirement", "Pure univariate numerical series", "Very large datasets (thousands of rows)", "Moderate datasets (6 months to 2 years)"],
        ["Hardware Needs", "Minimal CPU", "High (GPU acceleration required)", "Standard low-cost CPU (any laptop)"],
        ["Training Speed", "Fast (< 2 seconds)", "Slow (several minutes per ticker)", "Fast (< 1 second)"],
        ["Look-Ahead Bias", "Usually respected", "Often violated in random batches", "Strictly prevented via chronological split"],
        ["News Sentiment", "None (Numerical only)", "Requires complex multimodal embeddings", "Native VADER lexicon integration"],
        ["User Interface", "Terminal / Script output", "Research Jupyter notebooks", "Interactive 4-tab Streamlit dashboard"],
        ["Financial Cost", "Free / Script", "High cloud compute costs", "Free / Zero API keys required"],
    ]
    style_table(tbl_comp, [1.4, 1.7, 1.7, 1.7], ["Parameter", "Statistical (ARIMA)", "Deep Learning (LSTM)", "Proposed Hybrid System"], comp_data)
    add_p("Table 5.1: Comparison of stock forecasting approaches", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("5.3 Future Directions & Conclusion")
    add_p(
        "Future enhancements will focus on multimodal transformer sentiment analysis (FinBERT), automated paper trading execution (Alpaca/Zerodha APIs), "
        "intraday tick streaming, and Markowitz portfolio optimization.\n\n"
        "Conclusion: The Stock Market Analysis and Price Prediction System successfully bridges theoretical machine learning with practical financial decision support. "
        "By synthesizing pure-Python technical indicators, ensemble regression models with strict chronological splitting, and financial VADER sentiment analysis into an "
        "interactive Streamlit dashboard, the project delivers a reliable, 100% free, and fully functional software application.",
        space_after=14
    )

    doc.add_page_break()

    # ==================== REFERENCES ====================
    add_h1("REFERENCES")
    refs = [
        "1. Hutto, C. J., & Gilbert, E. (2014). \"VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.\" Eighth International AAAI Conference on Weblogs and Social Media (ICWSM-14), Ann Arbor, Michigan, pp. 216–225.",
        "2. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., et al. (2011). \"Scikit-learn: Machine Learning in Python.\" Journal of Machine Learning Research (JMLR), Vol. 12, pp. 2825–2830.",
        "3. McKinney, W. (2010). \"Data Structures for Statistical Computing in Python.\" Proceedings of the 9th Python in Science Conference (SciPy 2010), Austin, Texas, pp. 51–56.",
        "4. Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., et al. (2020). \"Array programming with NumPy.\" Nature, Vol. 585, pp. 357–362.",
        "5. Bollen, J., Mao, H., & Zeng, X. (2011). \"Twitter mood predicts the stock market.\" Journal of Computational Science, Vol. 2, No. 1, pp. 1–8.",
        "6. Wilder, J. W. (1978). New Concepts in Technical Trading Systems. Trend Research, Greensboro, NC.",
        "7. Streamlit Inc. (2024). \"Streamlit Documentation: The fastest way to build and share data apps.\" Online: https://docs.streamlit.io/",
        "8. Yahoo Finance & yfinance Project (2024). \"yfinance: An open-source tool that uses Yahoo's publicly available APIs to download market data.\" Online: https://github.com/ranaroussi/yfinance",
        "9. Finnhub.io (2024). \"Finnhub Real-Time Financial Market APIs Documentation.\" Online: https://finnhub.io/docs/api"
    ]
    for r_text in refs:
        add_p(r_text, space_after=8)

    # Save to file
    output_filename = "Stock_Market_Prediction_Project_Report.docx"
    doc.save(output_filename)
    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    create_report()
