#!/usr/bin/env python3
"""
Reducer: Daily Price Movement per Stock Symbol
Input:  symbol_date\topen\tclose  (sorted by key)
Output: symbol\tdate\topen\tclose\tchange\tpct_change
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split("\t")
            key = parts[0]
            open_price = float(parts[1])
            close_price = float(parts[2])

            # Split composite key back into symbol and date
            # Symbol may contain dots (e.g., BRK.B) but not underscores
            idx = key.rfind("_")
            if idx == -1:
                print(f"WARN: Bad key format: {key}", file=sys.stderr)
                continue

            symbol = key[:idx]
            date = key[idx + 1:]

            change = close_price - open_price
            if open_price != 0:
                pct_change = ((close_price - open_price) / open_price) * 100.0
            else:
                pct_change = 0.0

            print(f"{symbol}\t{date}\t{open_price:.4f}\t{close_price:.4f}\t{change:.4f}\t{pct_change:.4f}")

        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad reducer input: {e} — {line[:80]}",
                  file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
