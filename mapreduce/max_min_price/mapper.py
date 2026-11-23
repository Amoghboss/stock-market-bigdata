#!/usr/bin/env python3
"""
Mapper: Max High and Min Low Price per Stock Symbol
Input:  CSV lines — Date,Symbol,Company_Name,Open,High,Low,Close,Adj_Close,Volume
Output: symbol\thigh_price\tlow_price  (tab-separated)
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

            symbol = fields[1].strip()
            high_price = float(fields[4].strip())
            low_price = float(fields[5].strip())

            print(f"{symbol}\t{high_price}\t{low_price}")

        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad line: {e} — {line[:80]}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
