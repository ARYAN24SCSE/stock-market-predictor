"""
Data Loader Module for Stock Market Price Prediction
Handles fetching historical OHLCV data, company profile/metrics, and news headlines
from Yahoo Finance (zero API key) and optional Finnhub API.
"""

from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st
import yfinance as yf


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes yfinance DataFrame:
    - Flattens MultiIndex columns if present (e.g. from yfinance batch or recent updates)
    - Ensures standard columns: Open, High, Low, Close, Volume
    - Ensures DateTime index without timezone issues
    - Drops any rows where Close is NaN
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # If columns is MultiIndex (e.g., ('Close', 'AAPL')), flatten to single level
    if isinstance(df.columns, pd.MultiIndex):
        # Check if the first level contains standard OHLCV names
        first_level = [str(c[0]).capitalize() for c in df.columns]
        if any(col in ["Open", "High", "Low", "Close", "Volume"] for col in first_level):
            df.columns = [str(c[0]).capitalize() for c in df.columns]
        else:
            # Fallback: take the second level or join
            df.columns = [str(c[1]).capitalize() if len(c) > 1 else str(c[0]).capitalize() for c in df.columns]

    # Standardize column casing
    col_mapping = {col: str(col).capitalize() for col in df.columns}
    df.rename(columns=col_mapping, inplace=True)

    # Convert index to datetime if not already
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Remove timezone information for consistent plotting and calculations
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Sort index chronologically
    df.sort_index(inplace=True)

    # Drop duplicate index values if any
    df = df[~df.index.duplicated(keep="last")]

    # Check essential columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    available_cols = [c for c in required_cols if c in df.columns]
    
    if "Close" in df.columns:
        df.dropna(subset=["Close"], inplace=True)

    # Keep only available standard columns plus any existing ones
    return df


@st.cache_data(ttl=600, show_spinner=False)
def fetch_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetches historical stock data from Yahoo Finance between start_date and end_date.
    Includes caching for optimal performance.
    """
    try:
        # yfinance end date in download is exclusive, add 1 day to include end_date
        adj_end = end_date + timedelta(days=1)
        raw_df = yf.download(
            tickers=ticker.strip().upper(),
            start=start_date.strftime("%Y-%m-%d"),
            end=adj_end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=False
        )
        return clean_dataframe(raw_df)
    except Exception as e:
        st.error(f"Error fetching data for ticker '{ticker}': {e}")
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_company_info(ticker: str) -> dict:
    """
    Retrieves fundamental company info and metrics for the ticker.
    """
    defaults = {
        "shortName": ticker.upper(),
        "longName": ticker.upper(),
        "sector": "N/A",
        "industry": "N/A",
        "currency": "USD",
        "marketCap": 0,
        "currentPrice": 0.0,
        "fiftyTwoWeekHigh": 0.0,
        "fiftyTwoWeekLow": 0.0,
        "summary": "No description available.",
        "website": "",
    }

    try:
        t = yf.Ticker(ticker.strip().upper())
        info = t.info or {}
        return {
            "shortName": info.get("shortName") or info.get("longName") or ticker.upper(),
            "longName": info.get("longName") or info.get("shortName") or ticker.upper(),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "currency": info.get("currency", "USD"),
            "marketCap": info.get("marketCap", 0) or 0,
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice") or 0.0,
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0.0) or 0.0,
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0.0) or 0.0,
            "summary": info.get("longBusinessSummary", "No company summary available."),
            "website": info.get("website", ""),
        }
    except Exception:
        return defaults


@st.cache_data(ttl=600, show_spinner=False)
def fetch_stock_news(ticker: str, finnhub_api_key: str = "") -> list:
    """
    Fetches latest stock news headlines.
    Order of priority:
    1. Finnhub REST API (if user entered an API key)
    2. Yahoo Finance Search news (yf.Search)
    3. Google News RSS Feed (as guaranteed fallback, zero key required)
    Returns a list of dicts: [{'title': str, 'publisher': str, 'link': str, 'published': str, 'source_type': str}]
    """
    cleaned_ticker = ticker.strip().upper()
    news_items = []

    # 1. Try Finnhub if API key is provided
    if finnhub_api_key and finnhub_api_key.strip():
        try:
            today = datetime.now()
            from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")
            url = f"https://finnhub.io/api/v1/company-news?symbol={cleaned_ticker}&from={from_date}&to={to_date}&token={finnhub_api_key.strip()}"
            response = requests.get(url, timeout=6)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data[:15]:
                        headline = item.get("headline", "").strip()
                        if headline:
                            news_items.append({
                                "title": headline,
                                "publisher": item.get("source", "Finnhub"),
                                "link": item.get("url", "#"),
                                "published": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M") if item.get("datetime") else "Recent",
                                "source_type": "Finnhub API"
                            })
                    if news_items:
                        return news_items
        except Exception:
            pass

    # 2. Try yf.Search (Standard in yfinance modern versions)
    try:
        search = yf.Search(cleaned_ticker, news_count=12)
        if hasattr(search, "news") and search.news:
            for item in search.news:
                title = item.get("title", "")
                publisher = item.get("publisher", "Yahoo Finance")
                link = item.get("link", "#")
                pub_time = item.get("providerPublishTime")
                published_str = (
                    datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                    if pub_time
                    else "Recent"
                )
                if title:
                    news_items.append({
                        "title": title,
                        "publisher": publisher,
                        "link": link,
                        "published": published_str,
                        "source_type": "Yahoo Finance"
                    })
            if news_items:
                return news_items
    except Exception:
        pass

    # 3. Guaranteed Fallback: Google News RSS for the ticker
    try:
        import xml.etree.ElementTree as ET
        rss_url = f"https://news.google.com/rss/search?q={cleaned_ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(rss_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:12]:
                title = item.findtext("title", "")
                link = item.findtext("link", "#")
                pub_date = item.findtext("pubDate", "Recent")
                source = item.findtext("source", "Google News")
                if title:
                    news_items.append({
                        "title": title,
                        "publisher": source,
                        "link": link,
                        "published": str(pub_date)[:16],
                        "source_type": "Google News RSS"
                    })
    except Exception:
        pass

    return news_items
