# jarvis-data

Free daily market data feed for the Jarvis Trading Desk. A GitHub Actions robot pulls Yahoo Finance bars for stock index, gold, oil, treasury, and currency futures every weekday and saves them in `data/` so the desk's bots can paper trade every strategy on the shelf.

- `data/1m/` keeps 1 minute bars (Yahoo serves the last 7 days, so history grows from the day the feed starts)
- `data/5m/` keeps 5 minute bars (the first run backfills about 60 days)
- `data/1h/` keeps hourly bars (Yahoo serves about 2 years, so this adds out of sample history)
- `data/1d/` keeps daily bars (2 years)
- `data/last_update.json` says when the robot last ran and what it saved

Personal research use only. Data comes from Yahoo Finance and may contain gaps or errors.
