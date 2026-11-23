# Job 1: Average Closing Price per Symbol

## Description
Calculates the **average closing price** for each stock symbol across all trading days in the dataset.

## Input Format
CSV file with the following fields:
```
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
```

## Output Format
Tab-separated values:
```
symbol\tavg_close_price
```

## Sample Input
```csv
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
2023-01-03,AAPL,Apple Inc.,130.28,130.90,124.17,125.07,124.42,112117500
2023-01-04,AAPL,Apple Inc.,126.89,128.66,125.08,126.36,125.70,89113600
2023-01-03,MSFT,Microsoft Corp.,243.08,245.75,237.40,239.58,237.83,25391400
```

## Sample Output
```
AAPL	125.7150
MSFT	239.5800
```

## Execution Command
```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapper.py,reducer.py \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input /input/stock_data.csv \
  -output /output/average_price
```

## Local Testing
```bash
cat sample_data.csv | python3 mapper.py | sort -k1,1 | python3 reducer.py
```
