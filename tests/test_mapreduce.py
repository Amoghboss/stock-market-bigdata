"""
Automated Unit Tests: Hadoop MapReduce Jobs 1 through 7
Tests mapper emission, line parsing, header skipping, and reducer aggregation.
"""

import subprocess
import sys
import os
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_INPUT = """Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
2023-01-02,SYM_A,Corp A,100.0,105.0,98.0,102.0,102.0,10000
2023-01-03,SYM_A,Corp A,102.0,110.0,101.0,108.0,108.0,15000
2023-01-02,SYM_B,Corp B,200.0,205.0,195.0,202.0,202.0,20000
2023-01-03,SYM_B,Corp B,202.0,210.0,200.0,208.0,208.0,25000
"""

def run_mr_pipeline(job_folder, input_csv_data):
    mapper = str(PROJECT_ROOT / "mapreduce" / job_folder / "mapper.py")
    reducer = str(PROJECT_ROOT / "mapreduce" / job_folder / "reducer.py")
    sort_bin = "sort.exe" if os.name == "nt" else "sort"

    p_map = subprocess.Popen([sys.executable, mapper], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_sort = subprocess.Popen([sort_bin], stdin=p_map.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_map.stdout.close()
    p_red = subprocess.Popen([sys.executable, reducer], stdin=p_sort.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_sort.stdout.close()

    p_map.stdin.write(input_csv_data.encode("utf-8"))
    p_map.stdin.close()

    stdout, stderr = p_red.communicate(timeout=30)
    return stdout.decode("utf-8", errors="replace")

def test_job1_average_price():
    out = run_mr_pipeline("average_price", SAMPLE_INPUT)
    assert "SYM_A" in out
    assert "SYM_B" in out
    # SYM_A avg: (102 + 108)/2 = 105.0000
    assert "105.00" in out

def test_job2_max_min_price():
    out = run_mr_pipeline("max_min_price", SAMPLE_INPUT)
    assert "SYM_A" in out
    # SYM_A max high: 110.0, min low: 98.0
    assert "110.0" in out
    assert "98.0" in out

def test_job3_trading_volume():
    out = run_mr_pipeline("trading_volume", SAMPLE_INPUT)
    assert "SYM_A" in out
    # SYM_A total volume: 25000
    assert "25000" in out

def test_job4_daily_movement():
    out = run_mr_pipeline("daily_movement", SAMPLE_INPUT)
    assert "SYM_A" in out
    assert "2023-01-02" in out

def test_job5_monthly_trends():
    out = run_mr_pipeline("monthly_trends", SAMPLE_INPUT)
    assert "2023-01" in out

def test_job6_stock_ranking():
    out = run_mr_pipeline("stock_ranking", SAMPLE_INPUT)
    assert "Rank" in out
    assert "SYM_A" in out

def test_job7_volatility():
    out = run_mr_pipeline("volatility", SAMPLE_INPUT)
    assert "Annualized_Vol_Pct" in out
    assert "SYM_A" in out
