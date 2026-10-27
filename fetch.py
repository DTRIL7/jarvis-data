"""Jarvis data feed: pulls free Yahoo Finance futures and FX bars and keeps rolling CSVs.

Runs on GitHub Actions (free). Yahoo keeps about 7 days of 1 minute bars, 60 days of
5 minute bars, and years of daily bars, so running every weekday builds a growing history.
Output: data/<interval>/<SYM>.csv with header datetime,open,high,low,close,volume (UTC).
"""
import json, os, time, datetime as dt
import pandas as pd
import yfinance as yf

SYMS = {"ES": "ES=F", "NQ": "NQ=F", "RTY": "RTY=F", "GC": "GC=F", "CL": "CL=F",
        "ZN": "ZN=F", "6E": "6E=F", "6B": "6B=F", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X"}
PLAN = [("1m", "7d"), ("5m", "60d"), ("1h", "730d"), ("1d", "2y")]
OUT = "data"


def pull(ticker, interval, period, tries=4):
    for k in range(tries):
        try:
            df = yf.download(ticker, interval=interval, period=period, progress=False,
                             auto_adjust=False, prepost=True, threads=False)
            if df is not None and len(df):
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
                idx = pd.to_datetime(df.index)
                idx = idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")
                df.index = idx
                df.index.name = "datetime"
                return df.dropna(subset=["open", "high", "low", "close"])
        except Exception as e:
            print(f"  {ticker} {interval} try {k + 1} failed: {e}")
        time.sleep(5 * (k + 1))
    return None


def merge(path, new):
    if os.path.exists(path):
        old = pd.read_csv(path, index_col="datetime", parse_dates=True)
        old.index = pd.to_datetime(old.index, utc=True)
        new = pd.concat([old, new])
    new = new[~new.index.duplicated(keep="last")].sort_index()
    new.to_csv(path, date_format="%Y-%m-%dT%H:%M:%S+00:00", float_format="%.6f")
    return len(new)


def main():
    report = {"updated_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "files": {}, "failed": []}
    for interval, period in PLAN:
        os.makedirs(f"{OUT}/{interval}", exist_ok=True)
        for sym, tk in SYMS.items():
            df = pull(tk, interval, period)
            if df is None:
                report["failed"].append(f"{sym} {interval}")
                print(f"FAILED {sym} {interval}")
                continue
            n = merge(f"{OUT}/{interval}/{sym}.csv", df)
            report["files"][f"{interval}/{sym}"] = {"rows": n, "last_bar": df.index.max().isoformat()}
            print(f"ok {sym} {interval}: {len(df)} pulled, {n} total, last {df.index.max()}")
            time.sleep(1)
    with open(f"{OUT}/last_update.json", "w") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    main()
