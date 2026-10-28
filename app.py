"""
Stock Market Price Prediction & Analysis Dashboard
Built with Streamlit, Plotly, yfinance, scikit-learn, and vaderSentiment.
College-level, end-to-end financial data science application.
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data_loader import fetch_company_info, fetch_stock_data, fetch_stock_news
from indicators import add_all_indicators
from predictor import forecast_future, train_and_backtest
from sentiment import analyze_news_list

# Page Configuration
st.set_page_config(
    page_title="Stock Market Price Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1a1e29;
        border: 1px solid #2e384d;
        border-radius: 10px;
        padding: 12px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0f172a;
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        border: 1px solid #1e293b;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
        font-weight: 600;
    }
    /* Badge tags */
    .badge-bullish {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #22c55e;
        font-weight: 600;
    }
    .badge-bearish {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #ef4444;
        font-weight: 600;
    }
    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.2);
        color: #cbd5e1;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #94a3b8;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_currency(val: float, currency: str = "USD") -> str:
    """Formats numeric price with currency symbol."""
    sym = "$" if currency == "USD" else ("₹" if currency == "INR" else f"{currency} ")
    return f"{sym}{val:,.2f}"


def format_number(num: float) -> str:
    """Formats large financial figures to Trillion, Billion, Million."""
    if num >= 1e12:
        return f"{num / 1e12:.2f}T"
    elif num >= 1e9:
        return f"{num / 1e9:.2f}B"
    elif num >= 1e6:
        return f"{num / 1e6:.2f}M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f}K"
    return f"{num:.2f}"


# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/bullish.png",
        width=54,
    )
    st.title("Stock Prediction")
    st.caption("College-Level Data Science Project")
    st.markdown("---")

    # Quick Presets
    preset_tickers = ["AAPL", "NVDA", "MSFT", "GOOGL", "TSLA", "RELIANCE.NS", "TCS.NS"]
    selected_preset = st.selectbox(
        "⚡ Popular Presets",
        options=["Custom"] + preset_tickers,
        index=1,  # Default to AAPL
        help="Quickly pick popular US or Indian stock tickers",
    )

    if selected_preset != "Custom":
        ticker_input = selected_preset
    else:
        ticker_input = st.text_input(
            "Enter Stock Ticker",
            value="AAPL",
            help="Yahoo Finance symbol (e.g. AAPL, AMZN, INFY.NS)",
        )

    ticker = ticker_input.strip().upper()

    # Date Range
    st.markdown("#### 📅 Historical Date Range")
    default_start = datetime.today() - timedelta(days=730)  # 2 years
    default_end = datetime.today()

    date_range = st.date_input(
        "Select Range",
        value=(default_start, default_end),
        max_value=datetime.today(),
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = default_start
        end_date = default_end

    # ML Model Configuration
    st.markdown("#### 🤖 Machine Learning Model")
    model_choice = st.selectbox(
        "Regressor Algorithm",
        [
            "Random Forest Regressor",
            "Linear Regression",
            "Gradient Boosting Regressor",
        ],
        index=0,
    )

    forecast_days = st.slider(
        "Forecast Horizon (Business Days)",
        min_value=7,
        max_value=30,
        value=14,
        step=1,
        help="Number of future trading days to predict",
    )

    st.markdown("---")
    st.markdown("#### 🔑 Finnhub API Key (Optional)")
    finnhub_key = st.text_input(
        "Finnhub Key",
        value="",
        type="password",
        help="Free key from finnhub.io for live market news. If empty, falls back to free Yahoo Finance news automatically with zero keys required.",
    )
    if finnhub_key:
        st.success("Finnhub Key provided", icon="✅")
    else:
        st.info("Using free Yahoo Finance news", icon="ℹ️")


# ---------------- MAIN CONTENT AREA ----------------
st.title(f"📈 Stock Market Price Prediction & Analysis: {ticker}")

# Fetch historical data and company profile
with st.spinner(f"Fetching market data for {ticker}..."):
    df_raw = fetch_stock_data(ticker, start_date, end_date)
    company_info = fetch_company_info(ticker)

if df_raw.empty or len(df_raw) < 20:
    st.error(
        f"Could not retrieve historical data for ticker **{ticker}**. Please check ticker spelling or expand date range."
    )
    st.stop()

# Enrich data with technical indicators
df = add_all_indicators(df_raw)

# Pre-train ML model & generate multi-day forecast so predictions are immediately visible
with st.spinner(f"Computing AI Price Prediction with {model_choice}..."):
    ml_results = train_and_backtest(df, model_name=model_choice, train_ratio=0.80)
    forecast_df = pd.DataFrame()
    if ml_results.get("success"):
        forecast_df = forecast_future(
            df=df,
            model=ml_results["model"],
            feature_cols=ml_results["feature_cols"],
            forecast_days=forecast_days,
        )

# Calculate latest metrics
curr_price = float(df["Close"].iloc[-1])
prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else curr_price
price_change = curr_price - prev_price
price_pct_change = (price_change / prev_price) * 100.0 if prev_price != 0 else 0.0

currency = company_info.get("currency", "USD")
market_cap = company_info.get("marketCap", 0)
high_52 = company_info.get("fiftyTwoWeekHigh", df["High"].max())
low_52 = company_info.get("fiftyTwoWeekLow", df["Low"].min())
day_vol = float(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0

# Header Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        label="Current Close",
        value=format_currency(curr_price, currency),
        delta=f"{price_change:+.2f} ({price_pct_change:+.2f}%)",
    )
with col2:
    st.metric(
        label="Day Range (High / Low)",
        value=f"{format_currency(float(df['High'].iloc[-1]), currency)} / {format_currency(float(df['Low'].iloc[-1]), currency)}",
    )
with col3:
    st.metric(
        label="52-Week High",
        value=format_currency(high_52, currency),
    )
with col4:
    st.metric(
        label="52-Week Low",
        value=format_currency(low_52, currency),
    )
with col5:
    st.metric(
        label="Market Capitalization",
        value=format_number(market_cap) if market_cap else "N/A",
    )

# ---------------- TOP AI PREDICTION TARGET SUMMARY ----------------
if not forecast_df.empty:
    next_day_pred = float(forecast_df["Forecasted_Close"].iloc[0])
    target_pred = float(forecast_df["Forecasted_Close"].iloc[-1])
    next_diff = next_day_pred - curr_price
    next_pct = (next_diff / curr_price) * 100.0 if curr_price > 0 else 0.0
    target_diff = target_pred - curr_price
    target_pct = (target_diff / curr_price) * 100.0 if curr_price > 0 else 0.0
    trend_symbol = "🟢 BULLISH" if target_diff >= 0 else "🔴 BEARISH"
    trend_border = "#22c55e" if target_diff >= 0 else "#ef4444"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1.5px solid {trend_border}; border-radius: 12px; padding: 16px 22px; margin-top: 14px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <span style="font-size: 0.82rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em;">AI Forecast Horizon ({forecast_days} Trading Days)</span>
                    <h3 style="margin: 3px 0 0 0; color: #f9fafb; font-size: 1.45rem;">
                        {trend_symbol} &bull; Expected Target: <span style="color: {'#4ade80' if target_diff>=0 else '#f87171'};">{format_currency(target_pred, currency)}</span> 
                        <span style="font-size: 1.05rem; color: {'#4ade80' if target_diff>=0 else '#f87171'}; font-weight: 500;">({target_pct:+.2f}%)</span>
                    </h3>
                </div>
                <div style="display: flex; gap: 24px; text-align: right;">
                    <div>
                        <div style="font-size: 0.8rem; color: #9ca3af;">Next Trading Day</div>
                        <div style="font-size: 1.15rem; font-weight: 600; color: #f3f4f6;">{format_currency(next_day_pred, currency)} <span style="font-size: 0.9rem; color: {'#4ade80' if next_diff>=0 else '#f87171'};">({next_pct:+.2f}%)</span></div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #9ca3af;">Model Accuracy (MAPE)</div>
                        <div style="font-size: 1.15rem; font-weight: 600; color: #38bdf8;">{ml_results['metrics']['MAPE']:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #9ca3af;">Active Algorithm</div>
                        <div style="font-size: 1.05rem; font-weight: 500; color: #cbd5e1;">{model_choice}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 4 Organised Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Market Overview & Candlesticks",
        "📉 Technical Indicators",
        "🔮 ML Price Prediction & Backtest",
        "📰 News & Sentiment Analysis",
    ]
)

# ---------------- TAB 1: MARKET OVERVIEW & CANDLESTICKS ----------------
with tab1:
    st.subheader("Interactive Price & Volume Candlestick Chart")

    # Overlay Toggles
    overlay_col1, overlay_col2, overlay_col3, overlay_col4, overlay_col5 = st.columns(5)
    with overlay_col1:
        show_sma20 = st.checkbox("Show SMA (20)", value=True)
    with overlay_col2:
        show_sma50 = st.checkbox("Show SMA (50)", value=False)
    with overlay_col3:
        show_sma200 = st.checkbox("Show SMA (200)", value=False)
    with overlay_col4:
        show_bb = st.checkbox("Show Bollinger Bands", value=False)
    with overlay_col5:
        show_ai_forecast = st.checkbox("🔮 Overlay AI Future Forecast", value=True, help="Draws the AI predicted future price trajectory and 95% confidence corridor directly on this chart!")

    # Candlestick + Volume Subplot
    fig_candle = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25],
    )

    # Candlestick Trace
    fig_candle.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
        ),
        row=1,
        col=1,
    )

    # Overlays
    if show_sma20 and "SMA_20" in df.columns:
        fig_candle.add_trace(
            go.Scatter(
                x=df.index,
                y=df["SMA_20"],
                name="SMA 20",
                line=dict(color="#38bdf8", width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_sma50 and "SMA_50" in df.columns:
        fig_candle.add_trace(
            go.Scatter(
                x=df.index,
                y=df["SMA_50"],
                name="SMA 50",
                line=dict(color="#f59e0b", width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_sma200 and "SMA_200" in df.columns:
        fig_candle.add_trace(
            go.Scatter(
                x=df.index,
                y=df["SMA_200"],
                name="SMA 200",
                line=dict(color="#a855f7", width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_bb and "BB_Upper" in df.columns and "BB_Lower" in df.columns:
        fig_candle.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"],
                name="BB Upper",
                line=dict(color="rgba(148, 163, 184, 0.4)", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig_candle.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Lower"],
                name="BB Lower",
                line=dict(color="rgba(148, 163, 184, 0.4)", width=1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(148, 163, 184, 0.08)",
            ),
            row=1,
            col=1,
        )

    # AI Forecast Overlay directly on the main candlestick chart
    if show_ai_forecast and not forecast_df.empty:
        connect_dates = [df.index[-1]] + list(forecast_df.index)
        connect_prices = [curr_price] + list(forecast_df["Forecasted_Close"])
        std_err = ml_results["metrics"]["RMSE"]
        upper_fc = [p + (1.96 * std_err) for p in connect_prices]
        lower_fc = [max(0, p - (1.96 * std_err)) for p in connect_prices]

        fig_candle.add_trace(
            go.Scatter(
                x=connect_dates,
                y=connect_prices,
                name=f"🔮 AI Forecast ({forecast_days}D)",
                line=dict(color="#10b981", width=3),
                mode="lines+markers",
                marker=dict(size=6, symbol="circle"),
            ),
            row=1,
            col=1,
        )
        fig_candle.add_trace(
            go.Scatter(
                x=connect_dates,
                y=upper_fc,
                name="AI 95% Upper Bound",
                line=dict(color="rgba(16, 185, 129, 0.3)", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig_candle.add_trace(
            go.Scatter(
                x=connect_dates,
                y=lower_fc,
                name="AI 95% Lower Bound",
                line=dict(color="rgba(16, 185, 129, 0.3)", width=1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(16, 185, 129, 0.12)",
            ),
            row=1,
            col=1,
        )
        # Annotation for Target Price
        fig_candle.add_annotation(
            x=connect_dates[-1],
            y=connect_prices[-1],
            text=f"AI Target: {format_currency(connect_prices[-1], currency)}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#10b981",
            font=dict(color="#ffffff", size=11),
            bgcolor="#047857",
            bordercolor="#10b981",
            borderwidth=1,
            row=1,
            col=1,
        )

    # Volume Trace
    if "Volume" in df.columns:
        vol_colors = [
            "#22c55e" if c >= o else "#ef4444"
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig_candle.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                marker_color=vol_colors,
                opacity=0.6,
            ),
            row=2,
            col=1,
        )

    fig_candle.update_layout(
        template="plotly_dark",
        height=620,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0b0f19",
    )
    fig_candle.update_yaxes(title_text=f"Price ({currency})", row=1, col=1)
    fig_candle.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig_candle, use_container_width=True)

    # Company Fundamentals & About Section
    with st.expander(f"🏢 About {company_info.get('longName', ticker)}", expanded=False):
        c_desc1, c_desc2 = st.columns([2, 1])
        with c_desc1:
            st.markdown(f"**Sector:** {company_info.get('sector', 'N/A')}")
            st.markdown(f"**Industry:** {company_info.get('industry', 'N/A')}")
            st.markdown(company_info.get("summary", "No summary available."))
        with c_desc2:
            st.markdown(f"**Currency:** {currency}")
            if company_info.get("website"):
                st.markdown(f"[🌐 Visit Official Website]({company_info.get('website')})")


# ---------------- TAB 2: TECHNICAL INDICATORS ----------------
with tab2:
    st.subheader("Oscillators & Momentum Indicators")

    # Subplot for RSI and MACD
    fig_ind = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Relative Strength Index (RSI - 14)", "MACD (12, 26, 9)"),
    )

    # 1. RSI
    if "RSI" in df.columns:
        fig_ind.add_trace(
            go.Scatter(
                x=df.index,
                y=df["RSI"],
                name="RSI (14)",
                line=dict(color="#38bdf8", width=2),
            ),
            row=1,
            col=1,
        )
        # Overbought (70) & Oversold (30)
        fig_ind.add_hline(
            y=70,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="Overbought (70)",
            row=1,
            col=1,
        )
        fig_ind.add_hline(
            y=30,
            line_dash="dash",
            line_color="#22c55e",
            annotation_text="Oversold (30)",
            row=1,
            col=1,
        )
        fig_ind.add_hrect(
            y0=70,
            y1=100,
            fillcolor="rgba(239, 68, 68, 0.08)",
            line_width=0,
            row=1,
            col=1,
        )
        fig_ind.add_hrect(
            y0=0,
            y1=30,
            fillcolor="rgba(34, 197, 94, 0.08)",
            line_width=0,
            row=1,
            col=1,
        )

    # 2. MACD
    if "MACD" in df.columns and "MACD_Signal" in df.columns:
        fig_ind.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD"],
                name="MACD Line",
                line=dict(color="#38bdf8", width=1.5),
            ),
            row=2,
            col=1,
        )
        fig_ind.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD_Signal"],
                name="Signal Line",
                line=dict(color="#f97316", width=1.5),
            ),
            row=2,
            col=1,
        )
        # Histogram
        hist_colors = [
            "#22c55e" if h >= 0 else "#ef4444"
            for h in df["MACD_Hist"]
        ]
        fig_ind.add_trace(
            go.Bar(
                x=df.index,
                y=df["MACD_Hist"],
                name="Histogram",
                marker_color=hist_colors,
            ),
            row=2,
            col=1,
        )

    fig_ind.update_layout(
        template="plotly_dark",
        height=580,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0b0f19",
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    )
    fig_ind.update_yaxes(title_text="RSI Score", range=[0, 100], row=1, col=1)
    fig_ind.update_yaxes(title_text="Value", row=2, col=1)

    st.plotly_chart(fig_ind, use_container_width=True)

    # Educational Indicator Interpretation Card
    st.info(
        """
        **💡 Viva Knowledge Nugget: Technical Indicator Interpretations**
        - **RSI (14):** Measures momentum on a 0-100 scale. RSI > 70 implies the asset is potentially overbought and due for consolidation/pullback. RSI < 30 indicates oversold conditions and potential bullish reversal.
        - **MACD (Moving Average Convergence Divergence):** Bullish momentum is signaled when the blue MACD line crosses above the orange Signal line. Bearish momentum triggers when it crosses below.
        - **Bollinger Bands:** 2-standard deviations around the 20-period moving average. Price hitting the upper band indicates high volatility and stretched valuation; lower band suggests oversold bounce opportunity.
        """,
        icon="📘",
    )


# ---------------- TAB 3: ML PRICE PREDICTION & BACKTEST ----------------
with tab3:
    st.subheader(f"Machine Learning Backtest & {forecast_days}-Day Future Forecast")

    if not ml_results.get("success"):
        st.warning(ml_results.get("error", "Error in ML pipeline."))
    else:
        metrics = ml_results["metrics"]

        # Educational & Visual Reading Guide
        st.markdown(
            f"""
            <div style="background-color: #1e293b; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 14px 18px; margin-bottom: 20px;">
                <h5 style="margin: 0 0 8px 0; color: #38bdf8;">📌 How to Read What the AI Predicted on the Charts:</h5>
                <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 0.92rem; line-height: 1.6;">
                    <li><strong>Chart 1 (Backtest Validation):</strong> The <span style="color: #f43f5e; font-weight: 600;">Pink Dashed Line</span> shows what the AI predicted on out-of-sample historical test days vs the <span style="color: #38bdf8; font-weight: 600;">Blue Solid Line</span> (actual real prices). A closer match indicates strong generalization.</li>
                    <li><strong>Chart 2 (Upcoming Future Forecast):</strong> The <span style="color: #10b981; font-weight: 600;">Bright Green Line with Markers</span> represents the AI's step-by-step forecasted price for the next <strong>{forecast_days} business days</strong>. The <span style="color: rgba(16, 185, 129, 0.7);">shaded green corridor</span> represents the 95% confidence interval (&plusmn;{format_currency(1.96 * metrics['RMSE'], currency)}).</li>
                    <li><strong>Tab 1 (Main Candlestick Chart):</strong> Enable the <em>"🔮 Overlay AI Future Forecast"</em> checkbox to see this exact trajectory projected directly beyond the latest candlestick!</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Metric Evaluation Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric(
                label="RMSE (Root Mean Sq Error)",
                value=f"{metrics['RMSE']:.2f}",
                help="Lower is better. Measures average magnitude of error in price units.",
            )
        with m_col2:
            st.metric(
                label="MAE (Mean Absolute Error)",
                value=f"{metrics['MAE']:.2f}",
                help="Average absolute deviation between actual and predicted prices.",
            )
        with m_col3:
            st.metric(
                label="MAPE (Mean Abs % Error)",
                value=f"{metrics['MAPE']:.2f}%",
                help="Percentage error relative to actual stock price. College benchmark < 5% is strong.",
            )
        with m_col4:
            st.metric(
                label="Directional Accuracy",
                value=f"{metrics['Directional_Accuracy']:.1f}%",
                help="Percentage of days the model correctly forecasted up vs. down direction.",
            )

        # Plot 1: Actual vs. Predicted on 20% Test Split
        st.markdown("#### 1. Out-of-Sample Test Set: Actual vs. Predicted Prices")
        y_test = ml_results["y_test"]
        y_pred = ml_results["y_pred"]

        fig_backtest = go.Figure()
        fig_backtest.add_trace(
            go.Scatter(
                x=y_test.index,
                y=y_test.values,
                name="Actual Test Price (Market Truth)",
                line=dict(color="#38bdf8", width=2.5),
            )
        )
        fig_backtest.add_trace(
            go.Scatter(
                x=y_pred.index,
                y=y_pred.values,
                name="AI Predicted Price (Model Output)",
                line=dict(color="#f43f5e", width=2.2, dash="dash"),
            )
        )

        fig_backtest.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0b0f19",
            xaxis_title="Date",
            yaxis_title=f"Price ({currency})",
            legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
        )
        st.plotly_chart(fig_backtest, use_container_width=True)

        # Multi-Day Future Price Forecast
        st.markdown(f"#### 2. Multi-Day Autoregressive Future Forecast ({forecast_days} Business Days)")

        if not forecast_df.empty:
            # Historical last 45 days + forecast
            recent_hist = df.iloc[-45:]

            fig_forecast = go.Figure()

            # Historical Line
            fig_forecast.add_trace(
                go.Scatter(
                    x=recent_hist.index,
                    y=recent_hist["Close"],
                    name="Recent Historical Close",
                    line=dict(color="#94a3b8", width=2),
                )
            )

            # Connect last point of historical to forecast
            connect_dates = [recent_hist.index[-1]] + list(forecast_df.index)
            connect_prices = [recent_hist["Close"].iloc[-1]] + list(forecast_df["Forecasted_Close"])

            fig_forecast.add_trace(
                go.Scatter(
                    x=connect_dates,
                    y=connect_prices,
                    name=f"AI {forecast_days}-Day Forecast",
                    line=dict(color="#10b981", width=3),
                    mode="lines+markers",
                    marker=dict(size=6, symbol="circle"),
                )
            )

            # Forecast confidence band estimation
            std_err = metrics["RMSE"]
            upper_band = [p + (1.96 * std_err) for p in connect_prices]
            lower_band = [max(0, p - (1.96 * std_err)) for p in connect_prices]

            fig_forecast.add_trace(
                go.Scatter(
                    x=connect_dates,
                    y=upper_band,
                    name="95% Upper Bound",
                    line=dict(color="rgba(16, 185, 129, 0.3)", width=1, dash="dot"),
                )
            )
            fig_forecast.add_trace(
                go.Scatter(
                    x=connect_dates,
                    y=lower_band,
                    name="95% Lower Bound",
                    line=dict(color="rgba(16, 185, 129, 0.3)", width=1, dash="dot"),
                    fill="tonexty",
                    fillcolor="rgba(16, 185, 129, 0.08)",
                )
            )

            # End Target Annotation
            fig_forecast.add_annotation(
                x=connect_dates[-1],
                y=connect_prices[-1],
                text=f"AI Target: {format_currency(connect_prices[-1], currency)}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#10b981",
                font=dict(color="#ffffff", size=11),
                bgcolor="#047857",
                bordercolor="#10b981",
                row=1,
                col=1,
            )

            fig_forecast.update_layout(
                template="plotly_dark",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="#0b0f19",
                plot_bgcolor="#0b0f19",
                xaxis_title="Date",
                yaxis_title=f"Price ({currency})",
                legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
            )
            st.plotly_chart(fig_forecast, use_container_width=True)

            # Detailed Day-by-Day Forecast Breakdown Table
            st.markdown("#### 3. Day-by-Day Forecast Breakdown")
            f_table = []
            for dt, row in forecast_df.iterrows():
                pred_p = float(row["Forecasted_Close"])
                diff_today = pred_p - curr_price
                diff_today_pct = (diff_today / curr_price) * 100.0 if curr_price > 0 else 0.0
                f_table.append({
                    "Date": dt.strftime("%Y-%m-%d (%a)"),
                    f"Predicted Close ({currency})": f"{pred_p:.2f}",
                    "Diff vs Today": f"{diff_today:+.2f}",
                    "Expected Return": f"{diff_today_pct:+.2f}%",
                    "Expected Movement": "🟢 Upward" if diff_today >= 0 else "🔴 Downward",
                })
            breakdown_df = pd.DataFrame(f_table)

            f_col1, f_col2 = st.columns([3, 1])
            with f_col1:
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            with f_col2:
                csv_data = forecast_df.to_csv().encode("utf-8")
                st.download_button(
                    label="📥 Download Forecast CSV",
                    data=csv_data,
                    file_name=f"{ticker}_forecast_{forecast_days}d.csv",
                    mime="text/csv",
                )
                st.caption(
                    f"Generated using {model_choice} with autoregressive lag feedback."
                )

        # Feature Importance / Weights (for tree models)
        if hasattr(ml_results["model"], "feature_importances_"):
            with st.expander("🔍 Feature Importance Explanations (Viva Ready)"):
                importances = ml_results["model"].feature_importances_
                fi_df = pd.DataFrame(
                    {"Feature": ml_results["feature_cols"], "Importance": importances}
                ).sort_values("Importance", ascending=True)

                fig_fi = go.Figure(
                    go.Bar(
                        x=fi_df["Importance"],
                        y=fi_df["Feature"],
                        orientation="h",
                        marker_color="#38bdf8",
                    )
                )
                fig_fi.update_layout(
                    template="plotly_dark",
                    title="Feature Contribution to Prediction",
                    height=360,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="#0b0f19",
                    plot_bgcolor="#0b0f19",
                )
                st.plotly_chart(fig_fi, use_container_width=True)


# ---------------- TAB 4: NEWS & SENTIMENT ANALYSIS ----------------
with tab4:
    st.subheader(f"News Headlines & VADER Sentiment Analysis for {ticker}")

    with st.spinner("Fetching and scoring news headlines..."):
        raw_news = fetch_stock_news(ticker, finnhub_api_key=finnhub_key)
        sentiment_res = analyze_news_list(raw_news)

    summary = sentiment_res["summary"]
    enriched_df = sentiment_res["enriched_df"]

    # Sentiment Score Gauge & Metrics
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)

    with s_col1:
        s_stance = summary["overall_sentiment"]
        badge_class = (
            "badge-bullish"
            if s_stance == "Bullish"
            else ("badge-bearish" if s_stance == "Bearish" else "badge-neutral")
        )
        st.markdown(
            f"""
            <div style="background-color: #1a1e29; border: 1px solid #2e384d; border-radius: 10px; padding: 16px; text-align: center;">
                <span style="font-size: 0.85rem; color: #94a3b8;">Market Sentiment Stance</span><br>
                <span class="{badge_class}" style="font-size: 1.25rem; display: inline-block; margin-top: 8px;">
                    {s_stance}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_col2:
        st.metric(
            label="Compound VADER Score",
            value=f"{summary['overall_score']:+.3f}",
            help="Scaled from -1.0 (Extreme Bearish) to +1.0 (Extreme Bullish)",
        )

    with s_col3:
        st.metric(
            label="Bullish Headlines",
            value=f"{summary['bullish_count']} ({summary['bullish_pct']}%)",
        )

    with s_col4:
        st.metric(
            label="Bearish Headlines",
            value=f"{summary['bearish_count']} ({summary['bearish_pct']}%)",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if enriched_df.empty:
        st.info("No recent news headlines available for this ticker at this time.")
    else:
        # Donut Chart for Sentiment Breakdown
        chart_col, info_col = st.columns([1, 2])
        with chart_col:
            labels = ["Bullish", "Neutral", "Bearish"]
            values = [
                summary["bullish_count"],
                summary["neutral_count"],
                summary["bearish_count"],
            ]
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.55,
                        marker_colors=["#22c55e", "#94a3b8", "#ef4444"],
                    )
                ]
            )
            fig_donut.update_layout(
                template="plotly_dark",
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#0b0f19",
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with info_col:
            st.markdown(
                f"""
                **Headline Data Source:** `{enriched_df['Source'].iloc[0] if not enriched_df.empty else 'Online API'}`  
                **Total Analyzed Items:** {summary['total_count']} headlines  
                **Lexicon Integration:** Standard VADER rules combined with custom financial domain lexicon weights (e.g., *surge, slump, rally, breakout, downgrade*).
                """
            )

        # News Table
        st.markdown("#### Scored News Headlines Feed")
        display_news_df = enriched_df[["Published", "Headline", "Source", "Sentiment", "Score"]].copy()
        st.dataframe(display_news_df, use_container_width=True, hide_index=True)


# Footer
st.markdown("---")
st.caption(
    "🎓 **Stock Market Price Prediction System** | Built with Python, Streamlit, Plotly, Scikit-Learn & VADER | Free Yahoo Finance Data."
)
