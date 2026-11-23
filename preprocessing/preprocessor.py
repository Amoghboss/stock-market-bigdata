#!/usr/bin/env python3
"""
Preprocessing Pipeline CLI & Orchestrator
Executes data validation, cleaning, and stores the processed dataset.
Can also upload cleaned datasets to Hadoop HDFS if configured.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.data_cleaner import StockDataCleaner

def run_preprocessing(input_path=None, output_path=None, fill_strategy="ffill"):
    """
    Main preprocessing execution function.
    """
    if input_path is None:
        input_path = PROJECT_ROOT / "datasets" / "raw" / "nse_stock_data.csv"
    else:
        input_path = Path(input_path)

    if output_path is None:
        output_dir = PROJECT_ROOT / "datasets" / "cleaned"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "cleaned_stock_data.csv"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(" STOCK MARKET BIG DATA PREPROCESSING PIPELINE")
    print("=" * 65)
    print(f"Input source:  {input_path}")
    print(f"Output target: {output_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found at: {input_path}. Please run dataset generation first.")

    cleaner = StockDataCleaner(input_path=input_path, output_path=output_path)
    report = cleaner.clean_all(fill_strategy=fill_strategy)
    saved_path = cleaner.save_cleaned_data(output_path)

    print("\n--- PREPROCESSING EXECUTION REPORT ---")
    print(f"  • Total Records Before Cleaning: {report.get('records_before', 0):,}")
    print(f"  • Duplicates Removed:            {report.get('duplicates_removed', 0):,}")
    print(f"  • Total Missing Values Found:    {report.get('total_missing_values', 0):,}")
    print(f"  • Missing Values Imputed:        {report.get('missing_values_filled', 0):,}")
    print(f"  • Invalid Price Records Fixed:   {report.get('invalid_prices', 0):,}")
    print(f"  • Invalid Volume Records Fixed:  {report.get('invalid_volumes', 0):,}")
    print(f"  • Total Outliers Flagged (IQR):  {report.get('total_outliers', 0):,}")
    print(f"  • Total Clean Records Output:    {report.get('records_after', 0):,}")
    print(f"  • Saved Cleaned Dataset:         {saved_path}")

    # Also save JSON report
    report_file = PROJECT_ROOT / "reports" / "preprocessing_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  • JSON Report Written:           {report_file}")
    print("=" * 65)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Market Data Preprocessing Pipeline")
    parser.add_argument("--input", default=None, help="Path to raw CSV file")
    parser.add_argument("--output", default=None, help="Path to save cleaned CSV file")
    parser.add_argument("--strategy", default="ffill", choices=["ffill", "bfill", "mean", "median", "drop"],
                        help="Missing value fill strategy")
    args = parser.parse_args()

    run_preprocessing(args.input, args.output, args.strategy)
