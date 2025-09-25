#!/usr/bin/env python3
import os
import time
import requests
import pandas as pd
import schedule

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# 1. Path to your input CSV (one ticker per line, no header)
CSV_PATH = "/Users/ravicorrie/Downloads/Stocks_list.csv"

# 2. Output CSV (where fetched data will be appended)
OUTPUT_CSV = "/Users/ravicorrie/Downloads/stock_data.csv"

# 3. Polygon API key & date range
API_KEY    = "z4y8Rj3dPztHiv0SVH2Co40OpFl9D23N"
START_DATE = "2024-01-01"   # ← change as needed (YYYY-MM-DD)
END_DATE   = "2024-12-31"   # ← change as needed (YYYY-MM-DD)

# 4. Batch size (number of tickers per run)
BATCH_SIZE = 5

# 5. File to remember where we left off
INDEX_FILE = "/Users/ravicorrie/Downloads/last_index.txt"

# ─── INITIAL SETUP ─────────────────────────────────────────────────────────────

# Read tickers (first column only), uppercase them
stockdf = pd.read_csv(
    CSV_PATH,
    header=None,
    names=["ticker"],
    usecols=[0]
)
stockdf["ticker"] = stockdf["ticker"].astype(str).str.upper()
tickers = stockdf["ticker"].tolist()

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# ─── STATE MANAGEMENT ──────────────────────────────────────────────────────────

def get_last_index():
    """Read the last processed index from file, or return 0 if missing."""
    if os.path.exists(INDEX_FILE):
        try:
            return int(open(INDEX_FILE).read().strip())
        except ValueError:
            pass
    return 0

def set_last_index(idx: int):
    """Save the next start index to file."""
    with open(INDEX_FILE, "w") as f:
        f.write(str(idx))

# ─── FETCH FUNCTION ────────────────────────────────────────────────────────────

def fetch_ticker(ticker: str) -> pd.DataFrame:
    """
    Fetch daily aggregates for one ticker from Polygon.
    Returns an empty DataFrame if no data.
    """
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}"
        f"/range/1/day/{START_DATE}/{END_DATE}"
    )
    params = {
        "adjusted": "true",
        "sort":     "asc",
        "limit":    5000,
        "apiKey":   API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json().get("results", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "t": "timestamp",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume"
        }, inplace=True)
        df["ticker"]    = ticker
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# ─── JOB LOGIC ─────────────────────────────────────────────────────────────────

def job():
    """Fetch the next batch of tickers and append new data to OUTPUT_CSV."""
    idx = get_last_index()
    batch = tickers[idx : idx + BATCH_SIZE]

    # wrap around if we've reached the end
    if not batch:
        idx = 0
        batch = tickers[idx : idx + BATCH_SIZE]

    print(f"=== Fetching batch at index {idx}: {batch} ===")
    fetched = []

    for tk in batch:
        try:
            df = fetch_ticker(tk)
            if not df.empty:
                fetched.append(df)
            else:
                print(f"  ⚠️ No data for {tk}")
        except Exception as e:
            print(f"  ❗ Error fetching {tk}: {e}")

    if not fetched:
        print("⚠️  No data fetched this run; skipping save.")
    else:
        new_data = pd.concat(fetched, ignore_index=True)

        # Filter out already-saved rows
        if os.path.isfile(OUTPUT_CSV):
            existing = pd.read_csv(OUTPUT_CSV, parse_dates=["timestamp"])
            merged = new_data.merge(
                existing[["timestamp", "ticker"]],
                on=["timestamp", "ticker"],
                how="left",
                indicator=True
            )
            to_append = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
        else:
            to_append = new_data

        if not to_append.empty:
            header = not os.path.isfile(OUTPUT_CSV)
            to_append.to_csv(OUTPUT_CSV, mode="a", header=header, index=False)
            print(f"✅ Appended {len(to_append)} new rows to {OUTPUT_CSV}")
        else:
            print("ℹ️  No new rows to append.")

    # Advance and save index for next run
    idx = idx + BATCH_SIZE
    if idx >= len(tickers):
        idx = 0
    set_last_index(idx)

    print(f"=== Job finished at {pd.Timestamp.now()} ===\n")

# ─── SCHEDULING ────────────────────────────────────────────────────────────────

# Run once at startup
job()

# Then schedule every minute
schedule.every(1).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
