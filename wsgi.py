#!/usr/bin/env python3
"""
Production WSGI Entrypoint for Stock Market Big Data Analytics Platform
Initializes pipeline datasets and database if not present, then exposes 'app' for Gunicorn.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure datasets and initial processing are present on first deploy
cleaned_data = PROJECT_ROOT / "datasets" / "cleaned" / "cleaned_stock_data.csv"
if not cleaned_data.exists():
    print("[DEPLOY INIT] Initializing datasets and preprocessing pipeline on first boot...")
    try:
        from datasets.generate_dataset import generate_all_data
        generate_all_data()
        from preprocessing.preprocessor import run_preprocessing
        run_preprocessing()
        from run import run_mapreduce_local
        run_mapreduce_local()
        from analytics.stock_analyzer import StockAnalyzer
        from analytics.report_generator import ReportGenerator
        analyzer = StockAnalyzer(cleaned_data)
        gen = ReportGenerator(analyzer)
        gen.generate_csv_report()
        gen.generate_pdf_report()
        print("[DEPLOY INIT] Pipeline initialization completed successfully!")
    except Exception as e:
        print(f"[DEPLOY INIT ERROR] {e}")

from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
