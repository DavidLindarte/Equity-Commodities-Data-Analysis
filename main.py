"""
Main controler.
Run Stock and news monitor .py each 60 seconds
Give sound notification
Create  CSV to be use in PB dashboards.

"""

import csv
import os
import subprocess
import time
from datetime import datetime
import monitor
import stocks

INTERVAL        = 15
CSV_FILE        = "results.csv"
NEWS_SPIKE      = 5
PRICE_UNCHANGED = 0.0

# ── State ─────────────────────────────────────────────────────────────────────

last_news_counts = {}

# ── Sound ─────────────────────────────────────────────────────────────────────

def play(message):
    """Speak an alert message using macOS built-in text-to-speech."""
    subprocess.call(["say", message])
    time.sleep(2)  # pause between alerts

# ── Alerts ────────────────────────────────────────────────────────────────────

def check_alerts(news_results, stock_results):
    global last_news_counts
    alerts = []

    for topic, count in news_results:
        if count is None:
            continue
        last = last_news_counts.get(topic)
        if last is not None and (count - last) >= NEWS_SPIKE:
            alerts.append(f"  ⚠ NEWS SPIKE   — '{topic}' grew by {count - last} articles ({last} → {count})")
            play(f"News spike. {topic}. {count - last} new articles.")
        last_news_counts[topic] = count

    for ticker, price, pct_avg, pct_last, avg in stock_results:
        if pct_last == PRICE_UNCHANGED:
            alerts.append(f"  ⚠ CONSIDERABLE MOVEMENT  — {ticker} price changed at ${price}")
            play(f"{ticker} not moving. Price {price}.")

    if alerts:
        print(f"\n  {'─'*46}")
        print("  ALERTS")
        print(f"  {'─'*46}")
        for a in alerts:
            print(a)

# ── CSV ───────────────────────────────────────────────────────────────────────

def save(timestamp, news_results, stock_results):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "type", "name",
                "value", "pct_vs_avg", "pct_vs_last","avg"
            ])
        for topic, count in news_results:
            writer.writerow([timestamp, "news", topic, count, "", ""])
        for ticker, price, pct_avg, pct_last, avg in stock_results:
            writer.writerow([timestamp, "stock", ticker, price, pct_avg, pct_last or "",avg])

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\nAI Stock + News Monitor — Ctrl+C to stop")
    raw   = input("Start date (YYYY-MM-DD): ").strip()
    start = datetime.strptime(raw, "%Y-%m-%d").date()

    print("\nSetting up stock averages...")
    stocks.setup(start)

    run_number = 0
    while True:
        run_number += 1
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*50}")
        print(f"  Run #{run_number}  —  {ts}")
        print(f"{'='*50}")

        print("\n  News")
        news_results = monitor.run(start)

        print("\n  Stocks")
        stock_results = stocks.run(start)

        check_alerts(news_results, stock_results)

        save(ts, news_results, stock_results)
        print(f"\n  Saved to {CSV_FILE}")
        print(f"  Next run in {INTERVAL}s  (Ctrl+C to stop)")

        try:
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\n\nStopped.")
            break

if __name__ == "__main__":
    main()
