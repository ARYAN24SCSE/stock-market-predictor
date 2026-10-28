# 📈 Stock Market Price Prediction & Analysis Dashboard

An end-to-end, college-grade financial data science and machine learning application developed in Python with **Streamlit**, **Plotly**, **Scikit-Learn**, **yfinance**, and **VADER Sentiment Analysis**.

The application operates **100% out-of-the-box using free market data** (zero mandatory API keys) and provides an optional Finnhub API integration for real-time live company news sentiment analysis.

---

## 🎯 1. Project Abstract
Financial market price movement analysis is notoriously challenging due to market volatility, non-linear relationships, and dynamic macroeconomic factors. This project implements a comprehensive decision-support system featuring:
1. **Interactive Market Exploration:** Historical candlestick charts with volume bars, Simple Moving Averages (SMA 20/50/200), and Bollinger Bands.
2. **Technical Indicator Oscillators:** Vectorized calculations for Relative Strength Index (RSI-14) and Moving Average Convergence Divergence (MACD).
3. **Machine Learning Predictive Modeling:** Time-series feature engineering (lagged prices, rolling averages, daily percentage returns, volatility) evaluated using strict **chronological train-test splitting** to completely prevent look-ahead bias and data leakage.
4. **Multi-Horizon Future Forecasting:** Autoregressive multi-step recursive price forecasting for 7 to 30 business days with estimated prediction bounds.
5. **Real-time News Sentiment Analysis:** Natural Language Processing (NLP) scoring using VADER augmented with financial market lexicons.

---

## 🏛️ 2. System Architecture

```
[ User Browser / Streamlit UI ]
               │
               ▼
   ┌───────────────────────┐
   │        app.py         │ ◄── Main Dashboard & 4-Tab Layout
   └───────────┬───────────┘
               │
   ┌───────────┼───────────────────────────┬───────────────────────────┐
   ▼           ▼                           ▼                           ▼
[ data_loader.py ]               [ indicators.py ]             [ predictor.py ]        [ sentiment.py ]
   │                               │                             │                       │
   ├─ yfinance Historical OHLCV    ├─ SMA (20, 50, 200)          ├─ Lagged Features      ├─ VADER NLP Engine
   ├─ MultiIndex Cleaner           ├─ EMA (20)                   ├─ Chronological Split  ├─ Financial Lexicon
   ├─ Company Fundamentals         ├─ RSI (14)                   ├─ Scikit-Learn Models  ├─ Bullish / Bearish
   └─ Finnhub News (Optional)      ├─ MACD & Signal              └─ Multi-day Forecast   └─ Headline Feed
                                   └─ Bollinger Bands
```

---

## 🔬 3. Methodology & Theoretical Foundation

### A. Data Preprocessing & MultiIndex Handling
Recent versions of `yfinance` download data formatted with multi-level column indexes when handling symbol batches. `data_loader.py` dynamically identifies column hierarchy, flattens multi-level indexes to standard `['Open', 'High', 'Low', 'Close', 'Volume']`, strips timezone anomalies, and removes duplicate date entries.

### B. Pure Pandas/NumPy Technical Indicators
To eliminate C++ compiler requirements (such as TA-Lib build failures on Windows), all indicator equations are implemented using pure, vectorized Pandas and NumPy:
- **Simple Moving Average (SMA):**
  $$\text{SMA}_k = \frac{1}{k} \sum_{i=0}^{k-1} P_{t-i}$$
- **Relative Strength Index (RSI - 14):**
  Calculated using Wilder's Exponential Smoothing to track momentum:
  $$\text{RSI} = 100 - \left(\frac{100}{1 + \text{RS}}\right) \quad \text{where} \quad \text{RS} = \frac{\text{Wilder Smoothed Gain}}{\text{Wilder Smoothed Loss}}$$
- **Moving Average Convergence Divergence (MACD):**
  $$\text{MACD Line} = \text{EMA}_{12}(\text{Close}) - \text{EMA}_{26}(\text{Close})$$
  $$\text{Signal Line} = \text{EMA}_9(\text{MACD Line})$$
  $$\text{Histogram} = \text{MACD Line} - \text{Signal Line}$$
- **Bollinger Bands:**
  $$\text{Upper Band} = \text{SMA}_{20} + (2 \times \sigma_{20})$$
  $$\text{Lower Band} = \text{SMA}_{20} - (2 \times \sigma_{20})$$

### C. Prevention of Look-Ahead Bias & Data Leakage
In time-series modeling, standard randomized cross-validation (`train_test_split(shuffle=True)`) causes severe **data leakage** because the model trains on future data points to predict past data points.
This project enforces a **strictly chronological 80% train / 20% test split**:
- **Train Set:** First 80% of historical dates.
- **Test Set:** Most recent 20% of historical dates.
- All rolling features are shifted by 1 day (`Close.shift(1)`), ensuring zero future information leaks into the feature row of day $t$.

### D. Multi-Step Autoregressive Forecasting
For future $N$-day horizons (7 to 30 business days):
1. The model predicts $P_{t+1}$ using known lags.
2. $P_{t+1}$ is appended to the historical price buffer.
3. Features for day $t+2$ are recomputed autoregressively.
4. Bounds checking prevents runaway divergent loops.

### E. Evaluation Metrics
- **Root Mean Squared Error (RMSE):** Penalizes large deviations heavily.
- **Mean Absolute Error (MAE):** Average price deviation in currency units.
- **Mean Absolute Percentage Error (MAPE):** Scale-independent percentage accuracy:
  $$\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^n \left| \frac{A_t - F_t}{A_t} \right|$$
- **Directional Accuracy (%):** Percentage of days where the predicted direction (Up/Down) matched actual direction.

---

## 🚀 4. Setup & Installation Guide

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed.

### Step 1: Clone or Navigate to the Project Folder
```bash
cd d:\RealEstateLeadGEN
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
py -3.11 -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Launch the Dashboard

You can start the local development server using **npm** or directly with **Streamlit**:

#### Option A: Using npm (Recommended)
```bash
npm run dev
# or: npm start
```

#### Option B: Using Python Streamlit
```bash
streamlit run app.py
```
The application will launch in your browser at `http://localhost:8501`.

---


## 🔑 5. Optional Free Finnhub API Key Setup

The dashboard works completely without any API key by pulling news from Yahoo Finance. If you wish to use live Finnhub news:
1. Visit [finnhub.io](https://finnhub.io) and register for a free account.
2. Copy your free API token from the dashboard.
3. In the Streamlit sidebar, expand **Finnhub API Key** and paste your token.

---

## 🎓 6. Academic Viva / Project Defense Q&A

**Q1: Why can't we use random train/test splitting for stock price prediction?**  
*Answer:* In financial time series, prices have strong temporal autocorrelation. Random splitting leaks future data into the training set (look-ahead bias), yielding unrealistically high test accuracy that fails completely in live deployment. Chronological splitting maintains real-world validity.

**Q2: What is the purpose of lagging features (Lags 1-5)?**  
*Answer:* Lags convert a sequential time-series forecasting problem into a tabular supervised learning format suitable for algorithms like Random Forest and Gradient Boosting.

**Q3: How does VADER sentiment analysis work on financial headlines?**  
*Answer:* VADER is a rule-based sentiment model that considers punctuation, capitalization, degree modifiers, and polarities. We extend its default dictionary with financial-specific keywords (`bullish`, `surge`, `slump`, `downgrade`, `plunge`) to accurately classify market context.

**Q4: Which evaluation metric is most relevant for non-technical stakeholders?**  
*Answer:* MAPE (Mean Absolute Percentage Error), because it expresses error as an intuitive percentage (e.g. 2.1% error) regardless of whether a stock is priced at \$10 or \$500.

---

## 👥 Contributors & Academic License
- **Project Title:** Stock Market Price Prediction & Analysis
- **Frameworks:** Python, Streamlit, Plotly, Scikit-Learn, yfinance, VADER
- **License:** MIT License (Open Source for Educational Use)
