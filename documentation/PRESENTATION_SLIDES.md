# Project Presentation: Large-Scale Stock Market Data Processing and Trend Analysis using Hadoop HDFS

---

## Slide 1: Title & Overview
- **Project Title**: Large-Scale Stock Market Data Processing and Trend Analysis using Hadoop HDFS
- **Domain**: Big Data Engineering, Quantitative Finance, Distributed Systems
- **Core Technologies**: Apache Hadoop 3.3.6, HDFS, MapReduce (Streaming), Python, Flask, Plotly.js, Chart.js

---

## Slide 2: The Big Data Challenge in Finance
- Unprecedented exponential growth in financial market transaction logs
- High dimensionality: Multi-year OHLCV time-series across hundreds of equities
- Latency and scaling failures of traditional relational database systems (RDBMS)
- Necessity for distributed storage, fault tolerance, and parallel compute nodes

---

## Slide 3: Proposed Architecture
- **Data Ingestion**: Raw CSV datasets uploaded to HDFS `/stock_market/raw_data/`
- **Data Preprocessing**: Validation, deduplication, missing value imputation, IQR outlier detection -> HDFS `/stock_market/cleaned_data/`
- **Distributed Computing**: 7 parallel Hadoop MapReduce jobs across YARN -> `/stock_market/processed_data/`
- **Quantitative Engine**: Technical indicator calculation (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Interactive UI**: Modern Apple-inspired responsive dashboard with real-time analytics

---

## Slide 4: HDFS Storage Architecture
```
/stock_market/
├── raw_data/           <- Unprocessed ingestion
├── cleaned_data/       <- Preprocessed & validated dataset
├── processed_data/     <- MapReduce output partitions (part-00000)
├── analysis_results/   <- Technical indicator models
└── reports/            <- Exported PDF & CSV files
```
- Replication factor: 1 (pseudo-distributed) or 3 (cluster)
- Block size: 128 MB for high sequential throughput

---

## Slide 5: The 7 Hadoop MapReduce Jobs
1. **Job 1**: Average Stock Price Analysis (`symbol -> avg_close`)
2. **Job 2**: Maximum & Minimum Price Analysis (`symbol -> (max_high, min_low)`)
3. **Job 3**: Trading Volume Analysis (`symbol -> total, avg, peak volume`)
4. **Job 4**: Daily Stock Movement (`symbol_date -> delta, percentage change`)
5. **Job 5**: Monthly Trend Analysis (`symbol_month -> monthly average price`)
6. **Job 6**: Stock Performance Ranking (`rank -> capital return percentage`)
7. **Job 7**: Historical Volatility Analysis (`symbol -> daily return std * sqrt(252)`)

---

## Slide 6: Data Cleaning & Preprocessing Results
- **Initial Raw Ingestion**: 19,614 records
- **Duplicates Removed**: 39 records
- **Missing Values Detected & Imputed**: 98 values (forward/backward fill)
- **Invalid Prices Fixed**: 31 records (High < Low violations)
- **Invalid Volumes Rectified**: 10 negative volume entries
- **Total Clean Records**: 19,575 records across 15 NSE stocks (2020-2024)

---

## Slide 7: Technical Indicator Mathematical Models
- **SMA-20 & SMA-50**: Trend direction smoothing
- **EMA-20**: Exponential weighting for recent price action
- **RSI-14 (Wilder's Smoothing)**: Momentum oscillator bounded between 0 and 100
- **MACD (12, 26, 9)**: Momentum divergence and histogram signal line
- **Bollinger Bands**: Mean volatility bands at $\pm 2\sigma$

---

## Slide 8: Interactive Dashboard Features
- **Overview**: Real-time KPI statistics cards, market valuation bar chart, volume distribution
- **Stock Analysis**: Plotly candlestick charts, date filters, multi-stock peer comparisons
- **Trend Analysis**: Moving average crossovers, RSI gauge, MACD histogram, and Bullish/Bearish badges
- **Big Data Processing**: HDFS cluster telemetry, DataNode storage info, live terminal inspector
- **Reports**: Instant export of publication-grade PDF and CSV reports

---

## Slide 9: Verification & Testing
- Automated test suite using **Pytest**
- **27 Passed, 1 Skipped (Live Cluster Test), 0 Failed** (100% Core Test Coverage)
- Validated: Preprocessing logic, MapReduce streaming pipes, indicator correctness, REST APIs

---

## Slide 10: Conclusion & Future Scope
- **Conclusion**: Built an end-to-end, functional Big Data financial analytics system powered by Hadoop HDFS and MapReduce.
- **Future Scope**:
  - Apache Spark / PySpark for in-memory iterative machine learning
  - Apache Kafka for live WebSocket tick ingestion
  - LSTM neural networks for predictive stock price forecasting
