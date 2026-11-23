#!/usr/bin/env python3
"""
Reducer: Stock Performance Ranking
Calculates the overall percentage return for each stock from start date to end date.
Ranks all stocks from highest performing to lowest performing.
Output: rank\tsymbol\tstart_date\tstart_price\tend_date\tend_price\treturn_pct
"""

import sys

def main():
    stock_data = {}  # symbol -> list of (date, price)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            symbol = parts[0].strip()
            date_str = parts[1].strip()
            price = float(parts[2].strip())

            if symbol not in stock_data:
                stock_data[symbol] = []
            stock_data[symbol].append((date_str, price))
        except (ValueError, IndexError):
            continue

    # Compute return for each symbol
    results = []
    for symbol, records in stock_data.items():
        if not records:
            continue
        # Sort by date chronologically
        records.sort(key=lambda x: x[0])
        start_date, start_price = records[0]
        end_date, end_price = records[-1]

        if start_price > 0:
            ret_pct = ((end_price - start_price) / start_price) * 100.0
        else:
            ret_pct = 0.0

        results.append({
            "symbol": symbol,
            "start_date": start_date,
            "start_price": start_price,
            "end_date": end_date,
            "end_price": end_price,
            "return_pct": ret_pct
        })

    # Sort descending by return_pct
    results.sort(key=lambda x: x["return_pct"], reverse=True)

    # Emit ranked results
    print("Rank\tSymbol\tStart_Date\tStart_Price\tEnd_Date\tEnd_Price\tReturn_Pct")
    for rank, item in enumerate(results, start=1):
        print(f"{rank}\t{item['symbol']}\t{item['start_date']}\t{item['start_price']:.2f}\t"
              f"{item['end_date']}\t{item['end_price']:.2f}\t{item['return_pct']:+.2f}%")

if __name__ == "__main__":
    main()
