#!/usr/bin/env python3
"""
Reducer: Monthly Trend Analysis
Input:  symbol\tYYYY-MM\tclose_price  (sorted by symbol and year_month)
Output: symbol\tyear_month\tavg_close\ttrading_days
"""

import sys

def main():
    current_key = None  # (symbol, year_month)
    total_close = 0.0
    count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            symbol = parts[0].strip()
            year_month = parts[1].strip()
            close_price = float(parts[2].strip())
            key = (symbol, year_month)
        except (ValueError, IndexError):
            continue

        if current_key and current_key != key:
            avg_close = total_close / count
            print(f"{current_key[0]}\t{current_key[1]}\t{avg_close:.2f}\t{count}")
            total_close = 0.0
            count = 0

        current_key = key
        total_close += close_price
        count += 1

    if current_key and count > 0:
        avg_close = total_close / count
        print(f"{current_key[0]}\t{current_key[1]}\t{avg_close:.2f}\t{count}")

if __name__ == "__main__":
    main()
