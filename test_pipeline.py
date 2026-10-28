"""
Pipeline Verification Script
Runs end-to-end tests on data fetching, technical indicators, ML prediction, and sentiment analysis.
"""

from datetime import datetime, timedelta
import sys

def run_tests():
    print("=" * 60)
    print("STEP 1: Testing imports...")
    try:
        import yfinance as yf
        import pandas as pd
        import numpy as np
        import sklearn
        import streamlit
        import plotly
        import vaderSentiment
        print(" [OK] All core libraries imported successfully.")
    except Exception as e:
        print(f" [FAIL] Import error: {e}")
        sys.exit(1)

    print("=" * 60)
    print("STEP 2: Testing data_loader.py on AAPL...")
    from data_loader import fetch_stock_data, fetch_company_info, fetch_stock_news
    end_d = datetime.today()
    start_d = end_d - timedelta(days=365)
    df = fetch_stock_data("AAPL", start_d, end_d)
    print(f" [OK] Fetched {len(df)} rows. Columns: {list(df.columns)}")
    assert not df.empty, "DataFrame should not be empty"
    assert "Close" in df.columns, "'Close' column must exist"
    assert not isinstance(df.columns, pd.MultiIndex), "Columns should not be MultiIndex"

    info = fetch_company_info("AAPL")
    print(f" [OK] Fetched company info: {info.get('shortName')} ({info.get('sector')})")

    news = fetch_stock_news("AAPL")
    print(f" [OK] Fetched {len(news)} news headlines.")

    print("=" * 60)
    print("STEP 3: Testing indicators.py...")
    from indicators import add_all_indicators
    df_ind = add_all_indicators(df)
    for col in ["SMA_20", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "MACD_Hist", "BB_Upper", "BB_Lower"]:
        assert col in df_ind.columns, f"Indicator column {col} missing"
    print(f" [OK] All indicators computed. Latest RSI: {df_ind['RSI'].iloc[-1]:.2f}")

    print("=" * 60)
    print("STEP 4: Testing predictor.py (ML Train, Backtest, Forecast)...")
    from predictor import train_and_backtest, forecast_future
    results = train_and_backtest(df_ind, model_name="Random Forest Regressor", train_ratio=0.8)
    assert results["success"], f"Model training failed: {results.get('error')}"
    metrics = results["metrics"]
    print(f" [OK] ML Training Successful!")
    print(f"      RMSE: {metrics['RMSE']:.2f}")
    print(f"      MAE:  {metrics['MAE']:.2f}")
    print(f"      MAPE: {metrics['MAPE']:.2f}%")
    print(f"      Directional Accuracy: {metrics['Directional_Accuracy']:.1f}%")

    forecast_df = forecast_future(df_ind, results["model"], results["feature_cols"], forecast_days=14)
    print(f" [OK] Generated {len(forecast_df)} forecast days. Next day predicted close: {forecast_df['Forecasted_Close'].iloc[0]:.2f}")
    assert len(forecast_df) == 14, "Should have 14 forecasted days"

    print("=" * 60)
    print("STEP 5: Testing sentiment.py...")
    from sentiment import analyze_news_list
    sent_res = analyze_news_list(news)
    summary = sent_res["summary"]
    print(f" [OK] Sentiment Analysis Complete: {summary['overall_sentiment']} (Score: {summary['overall_score']:+.2f})")
    print(f"      Bullish: {summary['bullish_count']}, Neutral: {summary['neutral_count']}, Bearish: {summary['bearish_count']}")

    print("=" * 60)
    print("ALL PIPELINE VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
