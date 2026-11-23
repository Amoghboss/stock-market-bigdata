# Job 4: Daily Price Movement per Symbol

## Description
Calculates the **daily price change** (close − open) and **percentage change** for each stock symbol on each trading day.

## Input Format
CSV file with the following fields:
```
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
```

## Output Format
Tab-separated values:
```
symbol\tdate\topen\tclose\tchange\tpct_change
```

## Sample Input
```csv
Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
2023-01-03,AAPL,Apple Inc.,130.28,130.90,124.17,125.07,124.42,112117500
2023-01-04,AAPL,Apple Inc.,126.89,128.66,125.08,126.36,125.70,89113600
```

## Sample Output
```
AAPL	2023-01-03	130.2800	125.0700	-5.2100	-3.9992
AAPL	2023-01-04	126.8900	126.3600	-0.5300	-0.4177
```

## Execution Command
```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapper.py,reducer.py \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input /input/stock_data.csv \
  -output /output/daily_movement
```

## Local Testing
```bash
cat sample_data.csv | python3 mapper.py | sort -k1,1 | python3 reducer.py
```
