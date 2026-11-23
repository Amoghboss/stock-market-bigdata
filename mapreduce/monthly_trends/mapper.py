#!/usr/bin/env python3
"""
Mapper: Monthly Trend Analysis
Input:  CSV lines — Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
Output: symbol\tYYYY-MM\tclose_price
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Skip header
        if line.startswith("Date,") or line.startswith("date,"):
            continue

        try:
            fields = line.split(",")
            if len(fields) < 9:
                continue

            date_str = fields[0].strip()
            symbol = fields[1].strip()
            close_price = float(fields[6].strip())

            # Extract Year-Month (e.g. 2023-05)
            year_month = date_str[:7]
            if len(year_month) == 7 and year_month[4] == "-":
                print(f"{symbol}\t{year_month}\t{close_price}")

        except (ValueError, IndexError) as e:
            print(f"WARN: Bad record: {e} - {line[:80]}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
