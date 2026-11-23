#!/usr/bin/env python3
"""
Reducer: Volatility Analysis
Computes historical daily returns and annualized volatility for each stock:
Annualized Volatility = std(daily_log_returns) * sqrt(252) * 100%
Output: symbol\tannualized_volatility_pct\tmean_daily_return_pct\tdaily_std_pct\tdays_analyzed
"""

import sys
import math

def main():
    current_symbol = None
    records = []  # list of (date, close_price)

    print("Symbol\tAnnualized_Vol_Pct\tMean_Daily_Return_Pct\tDaily_Std_Pct\tDays_Analyzed")

    def process_symbol(symbol, items):
        if len(items) < 2:
            return
        items.sort(key=lambda x: x[0])  # Sort chronologically

        returns = []
        for i in range(1, len(items)):
            p_prev = items[i - 1][1]
            p_curr = items[i][1]
            if p_prev > 0 and p_curr > 0:
                ret = math.log(p_curr / p_prev)
                returns.append(ret)

        if not returns:
            return

        n = len(returns)
        mean_ret = sum(returns) / n
        variance = sum((r - mean_ret) ** 2 for r in returns) / (n - 1) if n > 1 else 0.0
        daily_std = math.sqrt(variance)
        annualized_vol = daily_std * math.sqrt(252) * 100.0

        mean_ret_pct = mean_ret * 100.0
        daily_std_pct = daily_std * 100.0

        print(f"{symbol}\t{annualized_vol:.2f}%\t{mean_ret_pct:+.4f}%\t{daily_std_pct:.4f}%\t{n + 1}")

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
            close_price = float(parts[2].strip())
        except (ValueError, IndexError):
            continue

        if current_symbol and current_symbol != symbol:
            process_symbol(current_symbol, records)
            records = []

        current_symbol = symbol
        records.append((date_str, close_price))

    if current_symbol and records:
        process_symbol(current_symbol, records)

if __name__ == "__main__":
    main()
