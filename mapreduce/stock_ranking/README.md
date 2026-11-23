# MapReduce Job 6: Stock Performance Ranking

## Objective
Identifies high-performing and low-performing equities over the entire historical observation period by calculating the net capital appreciation / percentage return:
$$\text{Return (\%)} = \frac{\text{Closing Price}_{\text{final}} - \text{Closing Price}_{\text{initial}}}{\text{Closing Price}_{\text{initial}}} \times 100$$

## Mapper Implementation (`mapper.py`)
- **Input**: CSV lines from cleaned stock market dataset.
- **Output**: `symbol\tdate\tclose_price`

## Reducer Implementation (`reducer.py`)
- **Input**: Sorted lines of `symbol\tdate\tclose_price`.
- **Logic**: Aggregates records per stock, sorts by trading date, identifies initial and terminal market price, calculates return percentage, and ranks all stocks descending by capital return.
- **Output**: `Rank\tSymbol\tStart_Date\tStart_Price\tEnd_Date\tEnd_Price\tReturn_Pct`

## Execution Command
```bash
python mapper.py < ../../datasets/cleaned/cleaned_stock_data.csv | sort | python reducer.py
```
