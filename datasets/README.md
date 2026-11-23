# Stock Market Datasets

This directory contains the historical stock market data used in the Big Data processing pipeline.

## Dataset Structure

The data conforms to standard OHLCV financial records:

| Field | Type | Description |
|---|---|---|
| `Date` | String (`YYYY-MM-DD`) | Trading date |
| `Symbol` | String | Ticker symbol (e.g., RELIANCE, TCS) |
| `Company_Name` | String | Full registered company name |
| `Open` | Float | Opening price at market open (09:15 IST) |
| `High` | Float | Maximum price achieved during session |
| `Low` | Float | Minimum price reached during session |
| `Close` | Float | Closing price at market close (15:30 IST) |
| `Adj_Close` | Float | Price adjusted for dividends and stock splits |
| `Volume` | Integer | Total shares traded during the trading day |

## Supported Stocks (15 NSE Blue-Chip Equities)

1. **RELIANCE** — Reliance Industries Ltd (Energy/Telecom/Retail)
2. **TCS** — Tata Consultancy Services Ltd (IT Services)
3. **INFY** — Infosys Ltd (IT Services)
4. **HDFCBANK** — HDFC Bank Ltd (Banking & Finance)
5. **ICICIBANK** — ICICI Bank Ltd (Banking & Finance)
6. **HINDUNILVR** — Hindustan Unilever Ltd (FMCG)
7. **ITC** — ITC Ltd (FMCG/Conglomerate)
8. **SBIN** — State Bank of India (Public Sector Bank)
9. **BHARTIARTL** — Bharti Airtel Ltd (Telecommunications)
10. **KOTAKBANK** — Kotak Mahindra Bank Ltd (Banking)
11. **LT** — Larsen & Toubro Ltd (Infrastructure & Engineering)
12. **AXISBANK** — Axis Bank Ltd (Banking)
13. **BAJFINANCE** — Bajaj Finance Ltd (NBFC/Financials)
14. **MARUTI** — Maruti Suzuki India Ltd (Automotive)
15. **WIPRO** — Wipro Ltd (IT Services)

## Generating or Downloading Data

### Option A: Generate Synthetic Benchmark Data
```bash
python datasets/generate_dataset.py
```
This generates:
- `datasets/raw/nse_stock_data.csv`: ~18,700 trading records with realistic geometric Brownian motion and injected anomalies (missing values, duplicates, outliers) to validate Hadoop preprocessing.
- `datasets/sample/sample_stock_data.csv`: 100 clean records for rapid unit tests.

### Option B: Download Real Market Data from Yahoo Finance
```bash
python datasets/download_data.py
```
Requires `pip install yfinance`.
Downloads live historical data from Yahoo Finance under tickers such as `RELIANCE.NS`.
