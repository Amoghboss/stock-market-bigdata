"""
Automated Unit & Integration Tests: Preprocessing & Data Cleaning
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from preprocessing.data_cleaner import StockDataCleaner
from preprocessing.preprocessor import run_preprocessing

@pytest.fixture
def sample_raw_df():
    """Create sample dirty DataFrame with known anomalies."""
    data = [
        {"Date": "2023-01-01", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": 100.0, "High": 105.0, "Low": 98.0, "Close": 102.0, "Adj_Close": 102.0, "Volume": 1000},
        {"Date": "2023-01-02", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": 102.0, "High": 108.0, "Low": 101.0, "Close": 107.0, "Adj_Close": 107.0, "Volume": 1500},
        # Duplicate row
        {"Date": "2023-01-02", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": 102.0, "High": 108.0, "Low": 101.0, "Close": 107.0, "Adj_Close": 107.0, "Volume": 1500},
        # Missing value
        {"Date": "2023-01-03", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": np.nan, "High": 110.0, "Low": 104.0, "Close": 109.0, "Adj_Close": 109.0, "Volume": 2000},
        # Invalid High < Low
        {"Date": "2023-01-04", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": 109.0, "High": 90.0, "Low": 112.0, "Close": 95.0, "Adj_Close": 95.0, "Volume": 1200},
        # Negative volume
        {"Date": "2023-01-05", "Symbol": "TEST", "Company_Name": "Test Corp", "Open": 100.0, "High": 105.0, "Low": 98.0, "Close": 102.0, "Adj_Close": 102.0, "Volume": -500},
    ]
    return pd.DataFrame(data)

def test_missing_values_detection(sample_raw_df, tmp_path):
    csv_file = tmp_path / "test_dirty.csv"
    sample_raw_df.to_csv(csv_file, index=False)

    cleaner = StockDataCleaner(csv_file)
    missing = cleaner.detect_missing_values()
    assert "Open" in missing
    assert missing["Open"] == 1

def test_remove_duplicates(sample_raw_df, tmp_path):
    csv_file = tmp_path / "test_dirty.csv"
    sample_raw_df.to_csv(csv_file, index=False)

    cleaner = StockDataCleaner(csv_file)
    dups_removed = cleaner.remove_duplicates()
    assert dups_removed == 1
    assert len(cleaner.df) == 5

def test_validate_prices(sample_raw_df, tmp_path):
    csv_file = tmp_path / "test_dirty.csv"
    sample_raw_df.to_csv(csv_file, index=False)

    cleaner = StockDataCleaner(csv_file)
    invalid_prices = cleaner.validate_prices()
    assert len(invalid_prices) >= 1  # Should catch High < Low

def test_validate_volume(sample_raw_df, tmp_path):
    csv_file = tmp_path / "test_dirty.csv"
    sample_raw_df.to_csv(csv_file, index=False)

    cleaner = StockDataCleaner(csv_file)
    invalid_vols = cleaner.validate_volume()
    assert len(invalid_vols) >= 1  # Should catch negative volume

def test_clean_all_pipeline(sample_raw_df, tmp_path):
    csv_file = tmp_path / "test_dirty.csv"
    sample_raw_df.to_csv(csv_file, index=False)
    out_file = tmp_path / "test_clean.csv"

    cleaner = StockDataCleaner(csv_file, out_file)
    report = cleaner.clean_all()
    cleaner.save_cleaned_data(out_file)

    assert report["records_before"] == 6
    assert report["records_after"] > 0
    assert report["duplicates_removed"] == 1
    assert out_file.exists()
