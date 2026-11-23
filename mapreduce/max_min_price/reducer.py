#!/usr/bin/env python3
"""
Reducer: Max High and Min Low Price per Stock Symbol
Input:  symbol\thigh_price\tlow_price  (sorted by symbol)
Output: symbol\tmax_high\tmin_low
"""

import sys

def main():
    current_symbol = None
    max_high = float("-inf")
    min_low = float("inf")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split("\t")
            symbol = parts[0]
            high_price = float(parts[1])
            low_price = float(parts[2])
        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad reducer input: {e} — {line[:80]}",
                  file=sys.stderr)
            continue

        if current_symbol and current_symbol != symbol:
            print(f"{current_symbol}\t{max_high:.4f}\t{min_low:.4f}")
            max_high = float("-inf")
            min_low = float("inf")

        current_symbol = symbol
        if high_price > max_high:
            max_high = high_price
        if low_price < min_low:
            min_low = low_price

    # Emit the last symbol
    if current_symbol:
        print(f"{current_symbol}\t{max_high:.4f}\t{min_low:.4f}")

if __name__ == "__main__":
    main()
