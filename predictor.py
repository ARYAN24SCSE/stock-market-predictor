"""
Machine Learning Pipeline for Stock Price Prediction
Includes Feature Engineering, Chronological Train-Test Split (No Lookahead Bias),
Model Training (Random Forest, Linear Regression, Gradient Boosting),
Evaluation Metrics (RMSE, MAE, MAPE), and Multi-Day Future Forecasting.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error

from indicators import calculate_rsi


def build_ml_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Constructs feature matrix X and target y for stock price prediction.
    Features:
    - Lagged close prices (Lag 1 through 5)
    - Rolling moving averages (5, 10, 20 days)
    - Rolling volatility / standard deviation (10 days)
    - Daily percentage returns
    - RSI (14 days)
    - Volume change percentage
    """
    if df.empty or len(df) < 30:
        return pd.DataFrame(), []

    data = df.copy()

    # Lags
    for lag in range(1, 6):
        data[f"Close_Lag_{lag}"] = data["Close"].shift(lag)

    # Rolling indicators
    data["Roll_Mean_5"] = data["Close"].shift(1).rolling(5).mean()
    data["Roll_Mean_10"] = data["Close"].shift(1).rolling(10).mean()
    data["Roll_Mean_20"] = data["Close"].shift(1).rolling(20).mean()
    data["Roll_Std_10"] = data["Close"].shift(1).rolling(10).std()

    # Returns
    data["Return_1d"] = data["Close"].shift(1).pct_change()
    data["Return_5d"] = data["Close"].shift(1).pct_change(5)

    # Technical
    data["RSI_14"] = calculate_rsi(data, period=14).shift(1)

    # Volume lag
    if "Volume" in data.columns:
        data["Vol_Lag_1"] = data["Volume"].shift(1)
        data["Vol_Change"] = data["Volume"].shift(1).pct_change().fillna(0)
    else:
        data["Vol_Lag_1"] = 0
        data["Vol_Change"] = 0

    feature_cols = [
        "Close_Lag_1", "Close_Lag_2", "Close_Lag_3", "Close_Lag_4", "Close_Lag_5",
        "Roll_Mean_5", "Roll_Mean_10", "Roll_Mean_20", "Roll_Std_10",
        "Return_1d", "Return_5d", "RSI_14", "Vol_Lag_1", "Vol_Change"
    ]

    # Target is the current day's Close price
    data["Target"] = data["Close"]

    # Drop NaNs resulting from rolling/lag calculations
    clean_data = data.dropna(subset=feature_cols + ["Target"]).copy()

    return clean_data, feature_cols


def get_model_instance(model_name: str, random_state: int = 42):
    """Factory function for instantiating the selected ML regressor."""
    m_name = model_name.lower().replace(" ", "_")
    if "random_forest" in m_name:
        return RandomForestRegressor(
            n_estimators=120,
            max_depth=12,
            min_samples_split=4,
            random_state=random_state,
            n_jobs=-1
        )
    elif "gradient_boosting" in m_name:
        return GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=random_state
        )
    else:
        # Default to Linear Regression
        return LinearRegression()


def train_and_backtest(
    df: pd.DataFrame,
    model_name: str = "Random Forest Regressor",
    train_ratio: float = 0.8
) -> Dict:
    """
    Splits data chronologically (train_ratio % train, remainder test) to prevent data leakage.
    Fits the specified ML model, predicts on the test set, and calculates RMSE, MAE, and MAPE.
    Returns model, metrics, and test prediction series.
    """
    feat_df, feature_cols = build_ml_features(df)
    if feat_df.empty or len(feat_df) < 40:
        return {
            "success": False,
            "error": "Insufficient historical data points (minimum 40 required after indicators)."
        }

    # Chronological Split
    split_idx = int(len(feat_df) * train_ratio)
    train_df = feat_df.iloc[:split_idx]
    test_df = feat_df.iloc[split_idx:]

    X_train = train_df[feature_cols]
    y_train = train_df["Target"]

    X_test = test_df[feature_cols]
    y_test = test_df["Target"]

    # Instantiate and fit
    model = get_model_instance(model_name)
    model.fit(X_train, y_train)

    # Predict test split
    y_pred = model.predict(X_test)
    y_pred_series = pd.Series(y_pred, index=test_df.index, name="Predicted")

    # Evaluation Metrics
    rmse = float(root_mean_squared_error(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    mape = float(mean_absolute_percentage_error(y_test, y_pred) * 100.0)

    # Directional accuracy (% of correct up/down daily moves)
    actual_dir = np.sign(y_test.diff().dropna())
    pred_dir = np.sign(y_pred_series.diff().dropna())
    directional_acc = float((actual_dir == pred_dir).mean() * 100.0) if len(actual_dir) > 0 else 50.0

    return {
        "success": True,
        "model": model,
        "feature_cols": feature_cols,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred_series,
        "train_df": train_df,
        "test_df": test_df,
        "metrics": {
            "RMSE": rmse,
            "MAE": mae,
            "MAPE": mape,
            "Directional_Accuracy": directional_acc,
        }
    }


def forecast_future(
    df: pd.DataFrame,
    model,
    feature_cols: List[str],
    forecast_days: int = 14
) -> pd.DataFrame:
    """
    Performs recursive multi-step autoregressive price forecasting for `forecast_days` business days.
    Feeds predicted close prices into subsequent lag and rolling calculations.
    """
    if df.empty or model is None:
        return pd.DataFrame()

    feat_df, _ = build_ml_features(df)
    if feat_df.empty:
        return pd.DataFrame()

    last_date = df.index[-1]
    # Generate upcoming business days
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)

    # Keep a running list of close prices for autoregressive lag calculation
    # Using the last 60 actual close prices
    recent_closes = list(df["Close"].iloc[-60:].values)
    recent_vols = list(df["Volume"].iloc[-20:].values) if "Volume" in df.columns else [0] * 20

    forecasted_prices = []

    for i in range(forecast_days):
        # Extract lags from recent_closes (most recent is index -1)
        c_lag1 = recent_closes[-1]
        c_lag2 = recent_closes[-2] if len(recent_closes) >= 2 else c_lag1
        c_lag3 = recent_closes[-3] if len(recent_closes) >= 3 else c_lag2
        c_lag4 = recent_closes[-4] if len(recent_closes) >= 4 else c_lag3
        c_lag5 = recent_closes[-5] if len(recent_closes) >= 5 else c_lag4

        roll_5 = float(np.mean(recent_closes[-5:]))
        roll_10 = float(np.mean(recent_closes[-10:]))
        roll_20 = float(np.mean(recent_closes[-20:]))
        roll_std_10 = float(np.std(recent_closes[-10:]))

        ret_1d = (c_lag1 - c_lag2) / c_lag2 if c_lag2 != 0 else 0.0
        ret_5d = (c_lag1 - c_lag5) / c_lag5 if c_lag5 != 0 else 0.0

        # Approximate RSI for recent values
        diffs = np.diff(recent_closes[-15:])
        gains = [d for d in diffs if d > 0]
        losses = [-d for d in diffs if d < 0]
        avg_g = np.mean(gains) if len(gains) > 0 else 0.001
        avg_l = np.mean(losses) if len(losses) > 0 else 0.001
        rsi_approx = 100.0 - (100.0 / (1.0 + (avg_g / avg_l)))

        v_lag1 = recent_vols[-1] if len(recent_vols) > 0 else 0
        v_chg = 0.0

        feat_values = {
            "Close_Lag_1": c_lag1,
            "Close_Lag_2": c_lag2,
            "Close_Lag_3": c_lag3,
            "Close_Lag_4": c_lag4,
            "Close_Lag_5": c_lag5,
            "Roll_Mean_5": roll_5,
            "Roll_Mean_10": roll_10,
            "Roll_Mean_20": roll_20,
            "Roll_Std_10": roll_std_10,
            "Return_1d": ret_1d,
            "Return_5d": ret_5d,
            "RSI_14": rsi_approx,
            "Vol_Lag_1": v_lag1,
            "Vol_Change": v_chg,
        }

        row_df = pd.DataFrame([feat_values])[feature_cols]
        predicted_val = float(model.predict(row_df)[0])

        # Bounds check to avoid runaway divergence
        min_allowed = min(recent_closes[-20:]) * 0.70
        max_allowed = max(recent_closes[-20:]) * 1.30
        predicted_val = float(np.clip(predicted_val, min_allowed, max_allowed))

        forecasted_prices.append(predicted_val)
        recent_closes.append(predicted_val)
        recent_vols.append(v_lag1)

    return pd.DataFrame(
        {"Forecasted_Close": forecasted_prices},
        index=future_dates
    )
