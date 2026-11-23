"""
Pytest fixtures shared across all test modules.

Provides reusable test data and clients for:
- Sample stock DataFrames
- Flask test client
- Temporary CSV files
"""

import os
import sys
import tempfile
import pytest
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so imports like
# `from preprocessing.data_cleaner import DataCleaner` work regardless of
# how pytest is invoked.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ───────────────────────── DataFrame Fixtures ──────────────────────────────

@pytest.fixture
def sample_dataframe():
    """
    A realistic stock-market DataFrame with 20 trading days for two symbols.
    Contains clean data suitable for analytics calculations.
    """
    np.random.seed(42)
    dates = pd.bdate_range(start="2024-01-01", periods=20)
    records = []
    for symbol in ["RELIANCE", "TCS"]:
        base_price = 2500.0 if symbol == "RELIANCE" else 3500.0
        for i, date in enumerate(dates):
            open_price = base_price + np.random.uniform(-50, 50)
            close_price = open_price + np.random.uniform(-30, 30)
            high_price = max(open_price, close_price) + np.random.uniform(0, 20)
            low_price = min(open_price, close_price) - np.random.uniform(0, 20)
            volume = int(np.random.uniform(1_000_000, 10_000_000))
            records.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Symbol": symbol,
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(close_price, 2),
                "Volume": volume,
            })
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture
def sample_dataframe_single():
    """
    A single-symbol DataFrame (RELIANCE) with 30 rows — enough for
    SMA-20, EMA-26, RSI-14, and MACD calculations.
    """
    np.random.seed(99)
    dates = pd.bdate_range(start="2024-01-01", periods=30)
    base = 2500.0
    records = []
    for i, date in enumerate(dates):
        open_price = base + np.random.uniform(-50, 50)
        close_price = open_price + np.random.uniform(-30, 30)
        high_price = max(open_price, close_price) + np.random.uniform(0, 20)
        low_price = min(open_price, close_price) - np.random.uniform(0, 20)
        volume = int(np.random.uniform(1_000_000, 10_000_000))
        records.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Symbol": "RELIANCE",
            "Open": round(open_price, 2),
            "High": round(high_price, 2),
            "Low": round(low_price, 2),
            "Close": round(close_price, 2),
            "Volume": volume,
        })
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture
def dirty_dataframe():
    """
    A DataFrame intentionally laced with quality issues:
    - NaN values
    - Duplicate rows
    - Negative prices
    - High < Low violations
    - Negative volume
    - Extreme outlier prices
    """
    data = {
        "Date": [
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",
            "2024-01-05", "2024-01-05", "2024-01-06", "2024-01-07",
            "2024-01-08", "2024-01-09",
        ],
        "Symbol": [
            "RELIANCE", "RELIANCE", "RELIANCE", "RELIANCE",
            "RELIANCE", "RELIANCE", "RELIANCE", "RELIANCE",
            "RELIANCE", "RELIANCE",
        ],
        "Open": [2500.0, np.nan, 2520.0, -10.0, 2530.0, 2530.0, 2540.0, 2550.0, 2560.0, 99999.0],
        "High": [2550.0, 2510.0, 2560.0, 2500.0, 2570.0, 2570.0, 2580.0, 2590.0, 2600.0, 100000.0],
        "Low":  [2480.0, 2490.0, np.nan, 2480.0, 2510.0, 2510.0, 2520.0, 2530.0, 2700.0, 99900.0],
        "Close":[2540.0, 2500.0, 2550.0, 2490.0, 2560.0, 2560.0, 2570.0, np.nan, 2590.0, 99950.0],
        "Volume":[5000000, 6000000, 7000000, -100, 8000000, 8000000, 9000000, 10000000, 11000000, 12000000],
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


# ───────────────────────── Flask Test Client ───────────────────────────────

@pytest.fixture
def flask_test_client():
    """
    Create a Flask test client from the backend application.
    Yields the test client for use in API endpoint tests.
    """
    try:
        from backend.app import app
    except ImportError:
        pytest.skip("backend.app module not available")

    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client


# ───────────────────────── Temporary CSV File ──────────────────────────────

@pytest.fixture
def temp_csv_file(sample_dataframe):
    """
    Write the sample DataFrame to a temporary CSV file on disk.
    Returns the file path.  The file is cleaned up after the test.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as f:
        sample_dataframe.to_csv(f, index=False)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def temp_csv_file_dirty(dirty_dataframe):
    """
    Write the dirty DataFrame to a temporary CSV for preprocessing tests.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as f:
        dirty_dataframe.to_csv(f, index=False)
        path = f.name
    yield path
    os.unlink(path)
