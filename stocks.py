"""
Check Woodside and Shell stock prices on Yahoo Finance
07-Julio-2026
"""

import yfinance as yf
from datetime import datetime

TICKERS   = ["WDS", "SHEL"]
THRESHOLD = 2.0

# averages are computed once at startup and reused each run
_averages    = {}
_last_prices = {}


def setup(start):
    """Compute historical averages from start date. Called once by main.py."""
    for ticker in TICKERS:
        df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
        _averages[ticker]    = round(float(df["Close"].squeeze().mean()), 2)
        _last_prices[ticker] = None
        print(f"  {ticker} average since {start}: ${_averages[ticker]}")


def run(start):
    """Fetch current prices and print vs average and vs last check. Returns list of (ticker, price, pct_avg, pct_last)."""
    ts = datetime.now().strftime("%H:%M:%S")
    results = []
    for ticker in TICKERS:
        price    = round(float(yf.Ticker(ticker).fast_info["last_price"]), 2)
        avg      = _averages[ticker]
        pct_avg  = round((price - avg) / avg * 100, 2)
        last     = _last_prices[ticker]
        pct_last = round((price - last) / last * 100, 2) if last else None
        change   = f"vs last: {pct_last:+.2f}%" if pct_last is not None else "vs last: —"
        print(f"  [{ts}]  {ticker}  ${price}  avg ${avg} ({pct_avg:+.2f}%)  {change}")
        _last_prices[ticker] = price
        results.append((ticker, price, pct_avg, pct_last,avg))
    return results


# ── Standalone ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import time
    start = input("Start date (YYYY-MM-DD): ").strip()
    setup(start)
    print()
    while True:
        run(start)
        print()
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
