"""
Current version: Monitoring LNG news and Shell and Woodside CEO
07-Julio-2026
"""

import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, date
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

# ── Topics ────────────────────────────────────────────────────────────────────

TOPICS = [
    "LNG production offshore",
    "gas accident 2026",
    "communities strike oil",'lis westcott',"wael sawan australia"
]

# ── Setup ─────────────────────────────────────────────────────────────────────

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ── Functions ─────────────────────────────────────────────────────────────────

def fetch_count(topic, start):
    query = topic
    if start: query += f" after:{start}"
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    with urlopen(Request(url, headers=HEADERS), timeout=15, context=SSL_CONTEXT) as r:
        root = ET.fromstring(r.read())
    return len(root.findall(".//item"))


def run(start):
    """Run a single check for all topics and print results. Returns list of (topic, count)."""
    today = date.today()
    print(f"\n  From {start} to {today} (today)")
    print(f"  {'-'*40}")
    results = []
    for topic in TOPICS:
        try:
            count = fetch_count(topic, start)
            print(f"  {topic:<30} {count} articles")
            results.append((topic, count))
        except Exception as e:
            print(f"  {topic:<30} Error: {e}")
            results.append((topic, None))
    return results

# ── Standalone ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    raw = input("\nStart date (YYYY-MM-DD, blank for no limit): ").strip()
    start = datetime.strptime(raw, "%Y-%m-%d").date() if raw else None
    run(start)
    print()