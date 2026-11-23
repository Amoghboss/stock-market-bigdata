# Job 3: Trading Volume Analysis per Symbol

## Description
Calculates the **total volume**, **average daily volume**, and **maximum single-day volume** for each stock symbol.

## Input Format
CSV file with the following fields:
```
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
```

## Output Format
Tab-separated values:
```
symbol\ttotal_volume\tavg_volume\tmax_volume
```

## Sample Input
```csv
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
2023-01-03,AAPL,Apple Inc.,130.28,130.90,124.17,125.07,124.42,112117500
2023-01-04,AAPL,Apple Inc.,126.89,128.66,125.08,126.36,125.70,89113600
2023-01-05,AAPL,Apple Inc.,127.13,127.77,124.76,125.02,124.37,80962700
```

## Sample Output
```
AAPL	282193800	94064600.00	112117500
```

## Execution Command
```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapper.py,reducer.py \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input /input/stock_data.csv \
  -output /output/trading_volume
```

## Local Testing
```bash
cat sample_data.csv | python3 mapper.py | sort -k1,1 | python3 reducer.py
```
