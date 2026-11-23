#!/usr/bin/env python3
"""
Reducer: Average Closing Price per Stock Symbol
Input:  symbol\tclose_price  (sorted by symbol)
Output: symbol\tavg_close_price
"""

import sys

def main():
    current_symbol = None
    total_close = 0.0
    count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            symbol, close_price = line.split("\t", 1)
            close_price = float(close_price)
        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad reducer input: {e} — {line[:80]}",
                  file=sys.stderr)
            continue

        if current_symbol and current_symbol != symbol:
            # Emit result for the previous symbol
            avg = total_close / count
            print(f"{current_symbol}\t{avg:.4f}")
            total_close = 0.0
            count = 0

        current_symbol = symbol
        total_close += close_price
        count += 1

    # Emit the last symbol
    if current_symbol:
        avg = total_close / count
        print(f"{current_symbol}\t{avg:.4f}")

if __name__ == "__main__":
    main()
