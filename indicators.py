"""
Technical Indicators Calculation Module
Computes SMA (20, 50, 200), RSI (14), MACD (12, 26, 9), and Bollinger Bands (20, 2)
using pure vectorized Pandas and NumPy for maximum reliability and speed.
"""

import numpy as np
import pandas as pd


def calculate_sma(df: pd.DataFrame, window: int = 20, col: str = "Close") -> pd.Series:
    """Calculates Simple Moving Average (SMA) for the specified rolling window."""
    return df[col].rolling(window=window, min_periods=1).mean()


def calculate_ema(df: pd.DataFrame, span: int = 20, col: str = "Close") -> pd.Series:
    """Calculates Exponential Moving Average (EMA) for the specified span."""
    return df[col].ewm(span=span, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, period: int = 14, col: str = "Close") -> pd.Series:
    """
    Calculates Relative Strength Index (RSI-14) using Wilder's smoothed method.
    Normalized between 0 and 100.
    """
    delta = df[col].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    # Wilder's exponential moving average
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    col: str = "Close"
) -> pd.DataFrame:
    """
    Calculates MACD Line, Signal Line, and MACD Histogram.
    - MACD Line = 12-day EMA - 26-day EMA
    - Signal Line = 9-day EMA of MACD Line
    - Histogram = MACD Line - Signal Line
    """
    ema_fast = df[col].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df[col].ewm(span=slow_period, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_hist = macd_line - signal_line

    result = pd.DataFrame(
        {
            "MACD": macd_line,
            "MACD_Signal": signal_line,
            "MACD_Hist": macd_hist,
        },
        index=df.index
    )
    return result


def calculate_bollinger_bands(
    df: pd.DataFrame,
    window: int = 20,
    num_std: float = 2.0,
    col: str = "Close"
) -> pd.DataFrame:
    """
    Calculates Bollinger Bands:
    - Middle Band: 20-period Simple Moving Average
    - Upper Band: Middle Band + (num_std * standard deviation)
    - Lower Band: Middle Band - (num_std * standard deviation)
    """
    sma = df[col].rolling(window=window, min_periods=1).mean()
    rolling_std = df[col].rolling(window=window, min_periods=1).std().fillna(0.0)
    upper_band = sma + (num_std * rolling_std)
    lower_band = sma - (num_std * rolling_std)

    result = pd.DataFrame(
        {
            "BB_Middle": sma,
            "BB_Upper": upper_band,
            "BB_Lower": lower_band,
        },
        index=df.index
    )
    return result


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends all technical indicators directly onto the DataFrame.
    """
    if df.empty or "Close" not in df.columns:
        return df

    out = df.copy()
    out["SMA_20"] = calculate_sma(out, window=20)
    out["SMA_50"] = calculate_sma(out, window=50)
    out["SMA_200"] = calculate_sma(out, window=200)
    out["EMA_20"] = calculate_ema(out, span=20)
    out["RSI"] = calculate_rsi(out, period=14)

    macd_df = calculate_macd(out)
    out["MACD"] = macd_df["MACD"]
    out["MACD_Signal"] = macd_df["MACD_Signal"]
    out["MACD_Hist"] = macd_df["MACD_Hist"]

    bb_df = calculate_bollinger_bands(out)
    out["BB_Middle"] = bb_df["BB_Middle"]
    out["BB_Upper"] = bb_df["BB_Upper"]
    out["BB_Lower"] = bb_df["BB_Lower"]

    return out
