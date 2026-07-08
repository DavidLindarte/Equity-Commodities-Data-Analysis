# Equity-Commodities-Data-Analysis
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

## Files

| File | Description |
|---|---|
| `main.py` | Controller — runs everything, handles alerts and CSV |
| `monitor.py` | Google News RSS scraper |
| `stocks.py` | Real-time stock price fetcher |
| `visualize.py` | Plotly chart generator from CSV |

## Requirements

- Python 3.9+
- macOS (voice alerts use the built-in `say` command)
- No paid API keys needed

## Author

Built by [Your Name] — inspired by idiosyncratic risk and AI-driven 
market intelligence. Open to feedback and collaboration.
