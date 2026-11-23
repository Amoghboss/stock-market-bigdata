# MapReduce Job 5: Monthly Trend Analysis

## Objective
Aggregates daily closing prices across calendar months to produce monthly average benchmark prices and trading volume for trend identification and seasonality studies.

## Mapper Implementation (`mapper.py`)
- **Input**: CSV record (`Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume`)
- **Logic**: Filters header, parses `Date` to extract `YYYY-MM`, emits composite key-value.
- **Output Key**: `symbol\tYYYY-MM`
- **Output Value**: `close_price`

## Reducer Implementation (`reducer.py`)
- **Input**: Tab-delimited `symbol\tYYYY-MM\tclose_price` sorted by Hadoop Shuffle & Sort.
- **Logic**: Sums closing prices per stock per month and computes arithmetic mean.
- **Output**: `symbol\tyear_month\tavg_close\ttrading_days`

## Sample Execution
```bash
# Local testing via Unix pipes
python mapper.py < ../../datasets/sample/sample_stock_data.csv | sort | python reducer.py

# Hadoop Streaming cluster execution
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /stock_market/cleaned_data/cleaned_stock_data.csv \
  -output /stock_market/processed_data/monthly_trends \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py
```

## Sample Output
```
RELIANCE	2023-01	2450.35	21
RELIANCE	2023-02	2410.12	20
TCS	2023-01	3405.80	21
```
