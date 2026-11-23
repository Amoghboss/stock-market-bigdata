#!/usr/bin/env python3
"""
Real Historical Stock Market Data Downloader
Downloads historical daily stock data from Yahoo Finance for NSE stocks.
Falls back gracefully if yfinance is not installed or if there is no internet access.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# 15 major Indian companies on NSE (using .NS suffix for Yahoo Finance)
NSE_TICKERS = {
    "RELIANCE.NS": ("RELIANCE", "Reliance Industries Ltd"),
    "TCS.NS": ("TCS", "Tata Consultancy Services Ltd"),
    "INFY.NS": ("INFY", "Infosys Ltd"),
    "HDFCBANK.NS": ("HDFCBANK", "HDFC Bank Ltd"),
    "ICICIBANK.NS": ("ICICIBANK", "ICICI Bank Ltd"),
    "HINDUNILVR.NS": ("HINDUNILVR", "Hindustan Unilever Ltd"),
    "ITC.NS": ("ITC", "ITC Ltd"),
    "SBIN.NS": ("SBIN", "State Bank of India"),
    "BHARTIARTL.NS": ("BHARTIARTL", "Bharti Airtel Ltd"),
    "KOTAKBANK.NS": ("KOTAKBANK", "Kotak Mahindra Bank Ltd"),
    "LT.NS": ("LT", "Larsen & Toubro Ltd"),
    "AXISBANK.NS": ("AXISBANK", "Axis Bank Ltd"),
    "BAJFINANCE.NS": ("BAJFINANCE", "Bajaj Finance Ltd"),
    "MARUTI.NS": ("MARUTI", "Maruti Suzuki India Ltd"),
    "WIPRO.NS": ("WIPRO", "Wipro Ltd"),
}

def download_historical_data(start_date="2020-01-01", end_date="2024-12-31", output_dir=None):
    """
    Downloads historical OHLCV data from Yahoo Finance.
    """
    if output_dir is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base, "datasets", "raw")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "yahoo_stock_data.csv")

    try:
        import yfinance as yf
    except ImportError:
        print("[WARNING] 'yfinance' library is not installed.")
        print("To download real data from Yahoo Finance, run: pip install yfinance")
        print("Falling back to synthetic data generator (generate_dataset.py).")
        return None

    print(f"Connecting to Yahoo Finance to download {len(NSE_TICKERS)} stocks...")
    all_dfs = []

    for ticker, (symbol, comp_name) in NSE_TICKERS.items():
        print(f"  Downloading {symbol} ({ticker})...", end=" ")
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            if df.empty:
                print("Failed (Empty response)")
                continue

            df = df.reset_index()
            # Standardize column names
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
            df["Symbol"] = symbol
            df["Company_Name"] = comp_name
            
            # Ensure standard OHLCV
            df = df.rename(columns={
                "Stock Splits": "Splits",
                "Adj Close": "Adj_Close"
            })
            if "Adj_Close" not in df.columns:
                df["Adj_Close"] = df["Close"]

            df = df[["Date", "Symbol", "Company_Name", "Open", "High", "Low", "Close", "Adj_Close", "Volume"]]
            all_dfs.append(df)
            print(f"Success ({len(df)} rows)")
        except Exception as e:
            print(f"Error: {e}")

    if not all_dfs:
        print("[ERROR] No data could be downloaded from Yahoo Finance.")
        return None

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"\nSuccessfully saved real Yahoo Finance data to: {output_file}")
    print(f"Total records: {len(combined_df)}")
    return output_file

if __name__ == "__main__":
    download_historical_data()
