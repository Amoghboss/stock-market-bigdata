"""
Automated Unit & Integration Tests: Financial Analytics & Technical Indicators
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from analytics.technical_indicators import TechnicalIndicators
from analytics.stock_analyzer import StockAnalyzer

@pytest.fixture
def sample_stock_df():
    """Create 50 days of synthetic trading records for analytics tests."""
    dates = pd.date_range("2023-01-01", periods=60, freq="B").strftime("%Y-%m-%d")
    np.random.seed(42)
    prices = [100.0]
    for _ in range(59):
        prices.append(prices[-1] * (1 + np.random.normal(0.001, 0.015)))

    rows = []
    for d, p in zip(dates, prices):
        rows.append({
            "Date": d,
            "Symbol": "TEST_SYM",
            "Company_Name": "Test Equity Ltd",
            "Open": round(p * 0.99, 2),
            "High": round(p * 1.02, 2),
            "Low": round(p * 0.98, 2),
            "Close": round(p, 2),
            "Adj_Close": round(p, 2),
            "Volume": 100000
        })
    return pd.DataFrame(rows)

def test_sma_calculation(sample_stock_df):
    ti = TechnicalIndicators(sample_stock_df)
    sma_10 = ti.sma(period=10)
    assert len(sma_10) == len(sample_stock_df)
    assert sma_10.iloc[:9].isna().all()
    assert not np.isnan(sma_10.iloc[9])

def test_ema_calculation(sample_stock_df):
    ti = TechnicalIndicators(sample_stock_df)
    ema_10 = ti.ema(period=10)
    assert len(ema_10) == len(sample_stock_df)
    assert not np.isnan(ema_10.iloc[-1])

def test_rsi_bounds(sample_stock_df):
    ti = TechnicalIndicators(sample_stock_df)
    rsi_14 = ti.rsi(period=14)
    valid_rsi = rsi_14.dropna()
    assert (valid_rsi >= 0.0).all()
    assert (valid_rsi <= 100.0).all()

def test_macd_columns(sample_stock_df):
    ti = TechnicalIndicators(sample_stock_df)
    macd_df = ti.macd()
    assert "MACD" in macd_df.columns
    assert "Signal" in macd_df.columns
    assert "Histogram" in macd_df.columns

def test_bollinger_bands(sample_stock_df):
    ti = TechnicalIndicators(sample_stock_df)
    bb = ti.bollinger_bands(period=20)
    assert "BB_Upper" in bb.columns
    assert "BB_Lower" in bb.columns
    valid_bb = bb.dropna()
    assert (valid_bb["BB_Upper"] >= valid_bb["BB_Lower"]).all()

def test_stock_analyzer_summary(sample_stock_df, tmp_path):
    csv_file = tmp_path / "test_stocks.csv"
    sample_stock_df.to_csv(csv_file, index=False)

    analyzer = StockAnalyzer(csv_file)
    summary = analyzer.get_stock_summary("TEST_SYM")
    assert summary["symbol"] == "TEST_SYM"
    assert "percentage_return" in summary
    assert "annualized_volatility" in summary
    assert summary["trading_days"] == 60
