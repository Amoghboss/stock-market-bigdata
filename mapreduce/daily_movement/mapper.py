#!/usr/bin/env python3
"""
Mapper: Daily Price Movement per Stock Symbol
Input:  CSV lines — Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
Output: symbol_date\topen\tclose  (tab-separated)

The key is symbol_date so that sorting groups by (symbol, date).
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Skip CSV header
        if line.startswith("Date,") or line.startswith("date,"):
            continue

        try:
            fields = line.split(",")
            if len(fields) < 9:
                print(f"WARN: Skipping malformed line (too few fields): {line[:80]}",
                      file=sys.stderr)
                continue

            date = fields[0].strip()
            symbol = fields[1].strip()
            open_price = float(fields[3].strip())
            close_price = float(fields[6].strip())

            # Composite key: symbol_date (underscore is safe since symbols don't contain it)
            key = f"{symbol}_{date}"
            print(f"{key}\t{open_price}\t{close_price}")

        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad line: {e} — {line[:80]}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
