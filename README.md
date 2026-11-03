# Equity-Commodities-Data-Analysis

**Live dashboard:** https://davidlindarte.github.io/Equity-Commodities-Data-Analysis/

Real-time monitor that tracks stock prices and news volume from a custom start date, updating every 15 seconds.
What makes it special is the personalization:
📰 Add any news topic that could influence your stocks - using google news plataform.
📈 Choose which stocks to track - using Yahoo finance plataform
⏱ Set your own time range and update frequency - Select your volatility date range.
🔔 Get a voice alert explaining price and news changes in real time - AI running local and getting information Real time.
📊 Everything is logged to a CSV — ready to plug into Power BI dashboards instantly

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Hosted version (dashboard)

A scheduled GitHub Actions job (`.github/workflows/snapshot.yml`) runs `pipeline/snapshot.py` every 3 hours on weekdays. It checks Woodside (WDS) and Shell (SHEL) prices against their average since the start date, counts Google News articles for each topic in `monitor.py`, logs everything to `data/history.csv` (same columns as `results.csv`), flags price moves of 2% or more and news spikes of 5 or more articles, and refreshes the dashboard in `docs/`.

## Files

| File | Description |
|---|---|
| `main.py` | Controller — runs everything, handles alerts and CSV |
| `monitor.py` | Google News RSS scraper |
| `stocks.py` | Real-time stock price fetcher |
| `pipeline/snapshot.py` | Hosted snapshot for the dashboard (GitHub Actions) |
| `docs/index.html` | Dashboard (GitHub Pages) |

## Requirements

- Python 3.9+
- macOS (voice alerts use the built-in `say` command)
- No paid API keys needed

## Author

Built by David Lindarte — inspired by idiosyncratic risk and AI-driven 
market intelligence. Open to feedback and collaboration.
