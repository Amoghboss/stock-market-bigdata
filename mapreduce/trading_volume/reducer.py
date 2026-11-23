#!/usr/bin/env python3
"""
Reducer: Trading Volume Analysis per Stock Symbol
Input:  symbol\tvolume  (sorted by symbol)
Output: symbol\ttotal_volume\tavg_volume\tmax_volume
"""

import sys

def main():
    current_symbol = None
    total_volume = 0
    count = 0
    max_volume = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            symbol, volume = line.split("\t", 1)
            volume = int(volume)
        except (ValueError, IndexError) as e:
            print(f"WARN: Skipping bad reducer input: {e} — {line[:80]}",
                  file=sys.stderr)
            continue

        if current_symbol and current_symbol != symbol:
            avg = total_volume / count
            print(f"{current_symbol}\t{total_volume}\t{avg:.2f}\t{max_volume}")
            total_volume = 0
            count = 0
            max_volume = 0

        current_symbol = symbol
        total_volume += volume
        count += 1
        if volume > max_volume:
            max_volume = volume

    # Emit the last symbol
    if current_symbol:
        avg = total_volume / count
        print(f"{current_symbol}\t{total_volume}\t{avg:.2f}\t{max_volume}")

if __name__ == "__main__":
    main()
