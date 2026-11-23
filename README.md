# Large-Scale Stock Market Data Processing and Trend Analysis using Hadoop HDFS

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.3.6-66CCFF?style=flat&logo=apachehadoop&logoColor=black)](https://hadoop.apache.org)
[![HDFS](https://img.shields.io/badge/Storage-HDFS-FF6600?style=flat)](https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade Big Data analytics platform demonstrating how massive volumes of historical stock market time-series data are collected, stored in a distributed Hadoop HDFS filesystem, cleaned through data validation pipelines, processed using distributed Hadoop MapReduce jobs, analyzed with quantitative financial indicators, and visualized through a modern, responsive web dashboard.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [HDFS Directory Architecture](#hdfs-directory-architecture)
3. [Hadoop MapReduce Analytics Jobs](#hadoop-mapreduce-analytics-jobs)
4. [Financial & Quantitative Analytics](#financial--quantitative-analytics)
5. [Interactive Web Dashboard](#interactive-web-dashboard)
6. [Technology Stack](#technology-stack)
7. [Project Directory Layout](#project-directory-layout)
8. [Installation & Setup](#installation--setup)
9. [Execution Guide](#execution-guide)
10. [Automated Verification & Tests](#automated-verification--tests)
11. [Academic Documentation](#academic-documentation)

---

## Architecture Overview

```
[ Data Collection ]
        │  (15 NSE Stocks / 5 Years / 19,575+ OHLCV Records)
        ▼
[ Hadoop HDFS Raw Ingestion ] ──────► /stock_market/raw_data/
        │
        ▼
[ Data Preprocessing Pipeline ] ────► Missing Value Imputation, Deduplication,
        │                             Outlier Flagging (IQR), Price Validation
        ▼
[ Hadoop HDFS Cleaned Storage ] ────► /stock_market/cleaned_data/
        │
        ▼
[ Distributed Hadoop MapReduce ] ───► 7 Streaming Jobs (Average Price, Max/Min,
        │                             Volume, Daily Movement, Monthly Trends,
        │                             Stock Ranking, Historical Volatility)
        ▼
[ Hadoop HDFS Processed Store ] ────► /stock_market/processed_data/
        │
        ▼
[ Technical Indicator Engine ] ─────► SMA (20/50), EMA (20), RSI (14),
        │                             MACD (12/26/9), Bollinger Bands (20, 2σ)
        ▼
[ Flask REST API & SQLite Cache ] ──► 20+ Endpoints, Job Tracking, Telemetry
        │
        ▼
[ Interactive Apple-Style UI ] ─────► Plotly & Chart.js Visualizations, Light/Dark
```

---

## HDFS Directory Architecture

The Hadoop Distributed File System is organized according to Big Data best practices:

```
/stock_market/
├── raw_data/           # Raw ingested CSV stock datasets
├── cleaned_data/       # Preprocessed, validated, normalized datasets
├── processed_data/     # Distributed MapReduce partition outputs (part-00000)
│   ├── average_price/
│   ├── max_min_price/
│   ├── trading_volume/
│   ├── daily_movement/
│   ├── monthly_trends/
│   ├── stock_ranking/
│   └── volatility/
├── analysis_results/   # Materialized indicator tables and trend logs
└── reports/            # Exported analytics PDFs and CSV summaries
```

---

## Hadoop MapReduce Analytics Jobs

All 7 jobs utilize Hadoop Streaming protocol (`stdin` / `stdout`) with clean mapper-reducer separation:

| Job | Title | Mapper Phase | Reducer Phase | Output Format |
|---|---|---|---|---|
| **Job 1** | **Average Stock Price** | `symbol → close_price` | Arithmetic mean per stock | `symbol \t avg_close` |
| **Job 2** | **Max & Min Price** | `symbol → (high, low)` | Global max high & min low | `symbol \t max_high \t min_low` |
| **Job 3** | **Trading Volume** | `symbol → volume` | Sum, average, and peak volume | `symbol \t total \t avg \t max` |
| **Job 4** | **Daily Stock Movement** | `symbol_date → (open, close)` | Price delta & percentage change | `symbol \t date \t open \t close \t change \t pct` |
| **Job 5** | **Monthly Trend** | `symbol_month → close` | Monthly average closing price | `symbol \t year_month \t avg_close \t count` |
| **Job 6** | **Stock Performance Ranking** | `symbol → (date, close)` | Net capital return ranking | `rank \t symbol \t start_p \t end_p \t return%` |
| **Job 7** | **Volatility Analysis** | `symbol → (date, close)` | Log return dispersion & $\sigma \times \sqrt{252}$ | `symbol \t annualized_vol% \t mean_return \t std` |

---

## Financial & Quantitative Analytics

The platform implements standard quantitative finance metrics:

- **Simple Moving Average (SMA)**:
  $$\text{SMA}_k(t) = \frac{1}{k}\sum_{i=0}^{k-1} P_{t-i}$$
- **Exponential Moving Average (EMA)**:
  $$\text{EMA}_t = \alpha \cdot P_t + (1 - \alpha) \cdot \text{EMA}_{t-1}, \quad \alpha = \frac{2}{k + 1}$$
- **Relative Strength Index (RSI-14)**:
  $$\text{RSI} = 100 - \frac{100}{1 + \text{RS}}, \quad \text{RS} = \frac{\text{Smoothed Gain}}{\text{Smoothed Loss}}$$
  *(Overbought threshold: 70, Oversold threshold: 30)*
- **Moving Average Convergence Divergence (MACD)**:
  $$\text{MACD} = \text{EMA}_{12}(P) - \text{EMA}_{26}(P), \quad \text{Signal} = \text{EMA}_9(\text{MACD})$$
- **Bollinger Bands**:
  $$\text{Upper/Lower} = \text{SMA}_{20} \pm 2 \cdot \sigma_{20}$$
- **Annualized Historical Volatility**:
  $$\sigma_{\text{ann}} = \sqrt{\frac{1}{N-1}\sum_{t=1}^N (r_t - \bar{r})^2} \times \sqrt{252} \times 100\%$$

---

## Interactive Web Dashboard

A responsive dashboard inspired by modern financial interfaces:
- **Overview**: Real-time KPI cards, market valuation distributions, and performance leaderboard.
- **Stock Analysis**: Historical candlestick and line chart viewer with peer comparisons.
- **Trend & Indicators**: Dual-pane visualization of SMA/EMA crossovers, RSI gauge, and MACD histograms.
- **Big Data & Hadoop**: HDFS cluster telemetry, DataNode storage metrics, and live MapReduce terminal outputs.
- **Reports**: Instant download of executive PDF reports and analytical CSV summaries.

---

## Technology Stack

| Category | Technologies |
|---|---|
| **Big Data Platform** | Apache Hadoop 3.3.6, HDFS, Hadoop Streaming, YARN |
| **Backend & APIs** | Python 3.8+, Flask 2.3+, SQLite (WAL Mode), Flask-CORS |
| **Data Processing** | Pandas 2.0+, NumPy |
| **Visualization** | Plotly.js 2.27, Chart.js 4.4 |
| **Frontend UI** | HTML5, CSS3 Variables (Light/Dark), Font Awesome 6 |
| **Reporting & Testing** | FPDF2, Pytest 7.4+ |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git
- *(Optional for full Hadoop mode)*: WSL2 Ubuntu with Java 11

### Step 1: Clone and Install Dependencies
```bash
git clone https://github.com/your-username/stock-market-bigdata.git
cd stock-market-bigdata

# Install Python requirements
pip install -r requirements.txt
```

### Step 2 (Optional): Setup Hadoop on WSL2 Ubuntu
If executing on a distributed cluster or WSL2:
```bash
bash hadoop/scripts/setup_hadoop.sh
```

---

## Execution Guide

The platform includes a unified orchestrator script (`run.py`):

```bash
# 1. Generate 5-year historical dataset for 15 NSE stocks
python run.py generate

# 2. Run data validation, cleaning, and anomaly resolution
python run.py preprocess

# 3. Execute all 7 MapReduce jobs locally (simulates Hadoop Streaming)
python run.py mapreduce-local

# 4. Alternatively, execute on live Hadoop cluster (requires Hadoop daemons)
python run.py mapreduce-hadoop

# 5. Run quantitative analytics and generate PDF/CSV reports
python run.py analytics

# 6. Launch the interactive dashboard
python run.py dashboard
```
Open **`http://localhost:5000`** in any modern web browser.

To execute the entire end-to-end pipeline in one command:
```bash
python run.py all
```

---

## Automated Verification & Tests

To execute the automated validation suite:
```bash
python run.py test
```
Or directly with pytest:
```bash
python -m pytest tests -v
```
All 28 unit and integration test cases validate:
- Preprocessing missing value imputation, duplicate removal, price/volume checks
- Financial indicator calculations (SMA, EMA, RSI bounds, MACD, Bollinger Bands)
- MapReduce mapper and reducer input/output contracts
- Flask REST API endpoint responses and serialization
- HDFS connection management and failover

---

## Academic Documentation

For complete academic project documentation conforming to university guidelines, see:
[`documentation/ACADEMIC_REPORT.md`](documentation/ACADEMIC_REPORT.md).
