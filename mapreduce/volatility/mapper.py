#!/usr/bin/env python3
"""
Mapper: Volatility Analysis
Input:  CSV lines — Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
Output: symbol\tdate\tclose_price
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("Date,") or line.startswith("date,"):
            continue

        try:
            fields = line.split(",")
            if len(fields) < 9:
                continue

            date_str = fields[0].strip()
            symbol = fields[1].strip()
            close_price = float(fields[6].strip())

            print(f"{symbol}\t{date_str}\t{close_price}")

        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
