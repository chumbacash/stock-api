import yfinance as yf
import pandas as pd
import os
import time 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuration
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
BASE_DATA_DIR = './data'
INTERVAL = '30m'  # Valid 60m interval
MAX_INTRADAY_DAYS = 730  # Yahoo's maximum for intraday historical data

def get_valid_chunks(start_date, end_date, interval):
    """Calculate valid date ranges considering Yahoo's limits"""
    if interval in ['1d', '5d', '1wk', '1mo', '3mo']:
        return [(start_date, end_date)]
    
    # For intraday intervals, limit to 730 days max
    max_days = min((end_date - start_date).days, MAX_INTRADAY_DAYS)
    adjusted_start = end_date - timedelta(days=max_days)
    
    # Split into 60-day chunks (Yahoo's per-request limit)
    chunks = []
    current_start = adjusted_start
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=60), end_date)
        chunks.append((current_start, current_end))
        current_start = current_end
    return chunks

def fetch_historical_data(symbol, interval, years=2):  # Reduced default to 2 years
    """Fetch data with proper intraday limits"""
    end_date = datetime.now()
    start_date = end_date - relativedelta(years=years)
    
    chunks = get_valid_chunks(start_date, end_date, interval)
    all_data = []
    
    for chunk_start, chunk_end in chunks:
        try:
            data = yf.download(
                symbol,
                start=chunk_start,
                end=chunk_end,
                interval=interval,
                progress=False,
                timeout=30  # Increased timeout
            )
            if not data.empty:
                all_data.append(data)
            time.sleep(2)  # More conservative rate limiting
        except Exception as e:
            print(f"Error fetching {symbol} ({chunk_start.date()} to {chunk_end.date()}): {str(e)}")
            continue
    
    return pd.concat(all_data).drop_duplicates().sort_index() if all_data else pd.DataFrame()

def save_data(symbol, df, base_dir, interval):
    """Save data with improved validation"""
    if df.empty:
        print(f"No data to save for {symbol}")
        return
    
    interval_dir = interval.replace('m', 'min').replace('h', 'hour')
    save_path = os.path.join(base_dir, interval_dir)
    os.makedirs(save_path, exist_ok=True)
    
    filename = f"{symbol}_{interval}_{df.index[0].date()}_to_{df.index[-1].date()}.csv"
    filepath = os.path.join(save_path, filename)
    
    df.to_csv(filepath)
    print(f"Saved {len(df)} rows for {symbol} to {filepath}")

def main():
    print("Starting the data pipeline...")
    start_time = datetime.now()
    
    for symbol in SYMBOLS:
        print(f"\nProcessing {symbol} ({INTERVAL})...")
        
        # For intraday data, limit to 2 years max
        df = fetch_historical_data(symbol, INTERVAL, years=2)
        
        if not df.empty:
            save_data(symbol, df, BASE_DATA_DIR, INTERVAL)
            print(f"Data range: {df.index[0].date()} to {df.index[-1].date()}")
        else:
            print(f"Failed to fetch data for {symbol}")
    
    print(f"\nTotal execution time: {datetime.now() - start_time}")

if __name__ == "__main__":
    main()