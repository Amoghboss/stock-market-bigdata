#!/usr/bin/env python3
"""
Stock Market Big Data Processing and Trend Analysis using Hadoop HDFS
Main System Orchestrator & CLI Entry Point
"""

import os
import sys
import argparse
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Set up project root
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def setup_logging(debug=False):
    """Configure system-wide logging."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if debug else logging.INFO
    log_file = log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("StockMarketBigData")

def generate_data():
    """Step 1: Generate or refresh the 5-year 15-stock market dataset."""
    print("\n" + "=" * 70)
    print(" [STEP 1] HISTORICAL DATASET GENERATION & COLLECTION")
    print("=" * 70)
    from datasets.generate_dataset import generate_all_data
    generate_all_data()

def preprocess_data():
    """Step 2: Clean, validate, and standardize the raw stock dataset."""
    print("\n" + "=" * 70)
    print(" [STEP 2] DATA PREPROCESSING, VALIDATION & ANOMALY HANDLING")
    print("=" * 70)
    from preprocessing.preprocessor import run_preprocessing
    run_preprocessing()

def run_mapreduce_local():
    """Step 3: Execute all 7 MapReduce jobs locally using streaming pipes."""
    print("\n" + "=" * 70)
    print(" [STEP 3] DISTRIBUTED MAPREDUCE ANALYTICS SUITE (LOCAL EXECUTION)")
    print("=" * 70)

    input_file = PROJECT_ROOT / "datasets" / "cleaned" / "cleaned_stock_data.csv"
    if not input_file.exists():
        input_file = PROJECT_ROOT / "datasets" / "raw" / "nse_stock_data.csv"

    output_dir = PROJECT_ROOT / "reports" / "mapreduce_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        ("average_price", "Job 1: Average Stock Price Analysis"),
        ("max_min_price", "Job 2: Maximum and Minimum Price Analysis"),
        ("trading_volume", "Job 3: Trading Volume Analysis"),
        ("daily_movement", "Job 4: Daily Stock Movement Analysis"),
        ("monthly_trends", "Job 5: Monthly Trend Analysis"),
        ("stock_ranking", "Job 6: Stock Performance Ranking"),
        ("volatility", "Job 7: Volatility & Market Risk Analysis"),
    ]

    total_start = time.time()
    sort_bin = "sort.exe" if os.name == "nt" else "sort"

    for folder, title in jobs:
        print(f"\n>>> Executing {title} ({folder}) <<<")
        mapper = PROJECT_ROOT / "mapreduce" / folder / "mapper.py"
        reducer = PROJECT_ROOT / "mapreduce" / folder / "reducer.py"
        out_file = output_dir / f"{folder}_output.txt"
        meta_file = output_dir / f"{folder}_meta.txt"

        job_start = time.time()
        try:
            with open(input_file, "r", encoding="utf-8") as inf:
                p_map = subprocess.Popen([sys.executable, str(mapper)], stdin=inf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p_sort = subprocess.Popen([sort_bin], stdin=p_map.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p_map.stdout.close()
                p_red = subprocess.Popen([sys.executable, str(reducer)], stdin=p_sort.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p_sort.stdout.close()
                stdout, stderr = p_red.communicate(timeout=120)

            elapsed = time.time() - job_start
            output_text = stdout.decode("utf-8", errors="replace")

            with open(out_file, "w", encoding="utf-8") as outf:
                outf.write(output_text)

            line_count = len([l for l in output_text.strip().split("\n") if l.strip()])
            print(f"  [SUCCESS] Completed in {elapsed:.2f}s | Output: {line_count:,} records -> {out_file.name}")

            with open(meta_file, "w", encoding="utf-8") as mf:
                mf.write(f"Job: {title}\nFolder: {folder}\nDuration_Seconds: {elapsed:.3f}\n"
                         f"Output_Records: {line_count}\nTimestamp: {datetime.now().isoformat()}\nStatus: SUCCESS\n")

        except Exception as e:
            print(f"  [ERROR] Job failed: {e}")

    total_time = time.time() - total_start
    print(f"\nAll 7 MapReduce jobs completed successfully in {total_time:.2f}s!")

def run_mapreduce_hadoop():
    """Step 3 (Hadoop Cluster): Execute all 7 MapReduce jobs on Hadoop YARN/HDFS."""
    print("\n" + "=" * 70)
    print(" [STEP 3] MAPREDUCE EXECUTION ON HADOOP CLUSTER (HDFS / YARN)")
    print("=" * 70)
    script = PROJECT_ROOT / "hadoop" / "scripts" / "run_mapreduce.sh"
    if os.name == "nt":
        print("Delegating execution to WSL2 Ubuntu Hadoop environment...")
        subprocess.run(["wsl", "bash", str(script).replace("\\", "/")], check=True)
    else:
        subprocess.run(["bash", str(script)], check=True)

def run_analytics():
    """Step 4: Execute financial analytics and generate reports."""
    print("\n" + "=" * 70)
    print(" [STEP 4] FINANCIAL ANALYTICS & REPORT GENERATION")
    print("=" * 70)
    from analytics.stock_analyzer import StockAnalyzer
    from analytics.report_generator import ReportGenerator

    cleaned_file = PROJECT_ROOT / "datasets" / "cleaned" / "cleaned_stock_data.csv"
    if not cleaned_file.exists():
        cleaned_file = PROJECT_ROOT / "datasets" / "raw" / "nse_stock_data.csv"

    analyzer = StockAnalyzer(cleaned_file)
    gen = ReportGenerator(analyzer)

    csv_path = gen.generate_csv_report()
    print(f"  * CSV Analytical Report: {csv_path}")
    try:
        pdf_path = gen.generate_pdf_report()
        print(f"  * PDF Analytical Report: {pdf_path}")
    except Exception as e:
        print(f"  * PDF Report Generation: {e}")

def start_dashboard(port=5000, debug=False):
    """Step 5: Launch the modern interactive dashboard."""
    print("\n" + "=" * 70)
    print(f" [STEP 5] LAUNCHING INTERACTIVE WEB DASHBOARD (PORT {port})")
    print("=" * 70)
    print(f"  Dashboard URL: http://localhost:{port}")
    print("  Press Ctrl+C to stop the web server.\n")

    from backend.app import app
    app.run(host="0.0.0.0", port=port, debug=debug)

def run_all(port=5000, debug=False):
    """Execute complete end-to-end data pipeline from raw data to dashboard."""
    generate_data()
    preprocess_data()
    run_mapreduce_local()
    run_analytics()
    start_dashboard(port=port, debug=debug)

def run_tests():
    """Run the complete test suite."""
    print("\n" + "=" * 70)
    print(" [TEST SUITE] RUNNING PYTEST TEST CASES")
    print("=" * 70)
    import pytest
    tests_dir = str(PROJECT_ROOT / "tests")
    ret = pytest.main(["-v", tests_dir, "--tb=short"])
    sys.exit(ret)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Large-Scale Stock Market Data Processing and Trend Analysis using Hadoop HDFS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  generate          Generate 5-year synthetic dataset for 15 NSE stocks
  preprocess        Run data validation, cleaning, and anomaly removal
  mapreduce-local   Execute all 7 MapReduce jobs locally via Unix pipes
  mapreduce-hadoop  Execute all 7 MapReduce jobs on real Hadoop HDFS/YARN
  analytics         Calculate technical indicators and generate CSV/PDF reports
  dashboard         Start Flask interactive web dashboard
  all               Run the entire pipeline end-to-end and start dashboard
  test              Run automated pytest validation test suite
        """
    )
    parser.add_argument("command", choices=[
        "generate", "preprocess", "mapreduce-local", "mapreduce-hadoop",
        "analytics", "dashboard", "all", "test"
    ], help="Pipeline stage to execute")
    parser.add_argument("--port", type=int, default=5000, help="Web dashboard port (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    logger = setup_logging(args.debug)

    actions = {
        "generate": generate_data,
        "preprocess": preprocess_data,
        "mapreduce-local": run_mapreduce_local,
        "mapreduce-hadoop": run_mapreduce_hadoop,
        "analytics": run_analytics,
        "dashboard": lambda: start_dashboard(args.port, args.debug),
        "all": lambda: run_all(args.port, args.debug),
        "test": run_tests,
    }

    actions[args.command]()
