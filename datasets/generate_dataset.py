#!/usr/bin/env python3
"""
Synthetic and Historical Stock Market Dataset Generator
Generates realistic 5-year historical trading data for 15 major Indian NSE stocks.
Includes deliberate anomalies (missing values, duplicates, outliers) to validate preprocessing.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Top 15 NSE stocks with realistic base prices and volatility profiles
STOCK_PROFILES = {
    "RELIANCE": {"name": "Reliance Industries Ltd", "base_price": 2200.0, "drift": 0.0004, "volatility": 0.016},
    "TCS": {"name": "Tata Consultancy Services Ltd", "base_price": 3200.0, "drift": 0.0003, "volatility": 0.014},
    "INFY": {"name": "Infosys Ltd", "base_price": 1450.0, "drift": 0.0003, "volatility": 0.018},
    "HDFCBANK": {"name": "HDFC Bank Ltd", "base_price": 1500.0, "drift": 0.0003, "volatility": 0.015},
    "ICICIBANK": {"name": "ICICI Bank Ltd", "base_price": 750.0, "drift": 0.0005, "volatility": 0.017},
    "HINDUNILVR": {"name": "Hindustan Unilever Ltd", "base_price": 2400.0, "drift": 0.0002, "volatility": 0.012},
    "ITC": {"name": "ITC Ltd", "base_price": 260.0, "drift": 0.0004, "volatility": 0.015},
    "SBIN": {"name": "State Bank of India", "base_price": 450.0, "drift": 0.0004, "volatility": 0.020},
    "BHARTIARTL": {"name": "Bharti Airtel Ltd", "base_price": 700.0, "drift": 0.0005, "volatility": 0.016},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank Ltd", "base_price": 1800.0, "drift": 0.0002, "volatility": 0.015},
    "LT": {"name": "Larsen & Toubro Ltd", "base_price": 1900.0, "drift": 0.0005, "volatility": 0.017},
    "AXISBANK": {"name": "Axis Bank Ltd", "base_price": 800.0, "drift": 0.0004, "volatility": 0.021},
    "BAJFINANCE": {"name": "Bajaj Finance Ltd", "base_price": 6200.0, "drift": 0.0005, "volatility": 0.024},
    "MARUTI": {"name": "Maruti Suzuki India Ltd", "base_price": 7500.0, "drift": 0.0003, "volatility": 0.018},
    "WIPRO": {"name": "Wipro Ltd", "base_price": 420.0, "drift": 0.0002, "volatility": 0.019},
}

def generate_trading_dates(start_date="2020-01-01", end_date="2024-12-31"):
    """Generate business days (Monday-Friday) between start and end dates."""
    dates = []
    curr = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    while curr <= end:
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
    return dates

def generate_stock_series(symbol, profile, dates):
    """Generate realistic OHLCV random walk with geometric Brownian motion."""
    records = []
    price = profile["base_price"]
    drift = profile["drift"]
    vol = profile["volatility"]

    for d in dates:
        # Daily return using geometric brownian motion
        ret = np.random.normal(drift, vol)
        close_price = max(10.0, price * np.exp(ret))
        
        # Intraday fluctuation
        open_price = price * (1 + np.random.normal(0, vol * 0.4))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, vol * 0.6)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, vol * 0.6)))
        low_price = max(1.0, low_price)
        adj_close = close_price * round(random.uniform(0.98, 1.0), 4)
        
        # Volume log-normally distributed
        base_vol = random.randint(500000, 5000000)
        vol_multiplier = 1.0 + abs(ret) * 10
        volume = int(base_vol * vol_multiplier)

        records.append({
            "Date": d,
            "Symbol": symbol,
            "Company_Name": profile["name"],
            "Open": round(open_price, 2),
            "High": round(high_price, 2),
            "Low": round(low_price, 2),
            "Close": round(close_price, 2),
            "Adj_Close": round(adj_close, 2),
            "Volume": volume
        })
        price = close_price

    return records

def inject_anomalies(df, missing_rate=0.005, duplicate_rate=0.002, outlier_rate=0.001):
    """
    Deliberately inject anomalies into raw data to allow testing data preprocessing module:
    - Missing values in numeric columns
    - Duplicate rows
    - Outliers / erroneous prices (e.g. High < Low, negative price)
    """
    df = df.copy()
    n = len(df)
    
    # 1. Duplicates
    dup_count = int(n * duplicate_rate)
    if dup_count > 0:
        sample_dups = df.sample(dup_count)
        df = pd.concat([df, sample_dups], ignore_index=True)
    
    # 2. Missing values
    missing_indices = random.sample(range(len(df)), int(len(df) * missing_rate))
    cols_to_nullify = ["Open", "Low", "Close", "Volume"]
    for idx in missing_indices:
        col = random.choice(cols_to_nullify)
        df.at[idx, col] = np.nan
        
    # 3. Outlier / Invalid records (inverted High/Low or negative volume)
    outlier_indices = random.sample(range(len(df)), int(len(df) * outlier_rate))
    for idx in outlier_indices:
        choice = random.choice(["invert_high_low", "negative_vol", "zero_price"])
        if choice == "invert_high_low":
            df.at[idx, "High"] = df.at[idx, "Low"] - 50.0  # Invalid High < Low
        elif choice == "negative_vol":
            df.at[idx, "Volume"] = -100000
        elif choice == "zero_price":
            df.at[idx, "Close"] = 0.0

    return df

def generate_all_data(output_dir=None):
    """Main generator function creating raw and sample datasets."""
    np.random.seed(42)
    random.seed(42)
    
    if output_dir is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_dir = os.path.join(base, "datasets", "raw")
        sample_dir = os.path.join(base, "datasets", "sample")
    else:
        raw_dir = os.path.join(output_dir, "raw")
        sample_dir = os.path.join(output_dir, "sample")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)

    print("Generating 5-year daily trading data for 15 NSE stocks (2020-2024)...")
    dates = generate_trading_dates("2020-01-01", "2024-12-31")
    print(f"Total trading days: {len(dates)}")

    all_records = []
    for symbol, profile in STOCK_PROFILES.items():
        records = generate_stock_series(symbol, profile, dates)
        all_records.extend(records)
        print(f"  Generated {len(records)} records for {symbol} ({profile['name']})")

    clean_df = pd.DataFrame(all_records)
    print(f"Total clean records generated: {len(clean_df)}")

    # Save clean sample (first 100 records)
    sample_file = os.path.join(sample_dir, "sample_stock_data.csv")
    clean_df.head(100).to_csv(sample_file, index=False)
    print(f"Sample dataset saved to: {sample_file} (100 records)")

    # Inject anomalies for the raw dataset
    raw_df = inject_anomalies(clean_df)
    raw_file = os.path.join(raw_dir, "nse_stock_data.csv")
    raw_df.to_csv(raw_file, index=False)
    print(f"Raw dataset with anomalies saved to: {raw_file} ({len(raw_df)} records)")

    # Print summary statistics
    print("\n--- Dataset Summary ---")
    print(f"Symbols: {list(STOCK_PROFILES.keys())}")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    print(f"Total Rows: {len(raw_df)}")
    print(f"Null values injected: {raw_df.isnull().sum().to_dict()}")

    return raw_file, sample_file

if __name__ == "__main__":
    generate_all_data()
