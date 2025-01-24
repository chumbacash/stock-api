import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configuration - Add validation
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
BASE_DATA_DIR = os.path.abspath('../data')  # Use absolute path
INTERVAL = '15m'
INTRADAY_LIMIT_DAYS = 60

# Validate interval first
VALID_INTERVALS = ['1m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']
if INTERVAL not in VALID_INTERVALS:
    raise ValueError(f"Invalid interval {INTERVAL}. Use: {VALID_INTERVALS}")

def get_valid_date_range(interval):
    """Add timezone awareness and logging"""
    print(f"Calculating date range for {interval}...")
    end_date = datetime.now()
    
    if interval in ['1m', '5m', '15m', '30m', '60m', '90m', '1h']:
        start_date = end_date - timedelta(days=INTRADAY_LIMIT_DAYS)
        # Ensure we get market hours only
        start_date = start_date.replace(hour=9, minute=30)
        end_date = end_date.replace(hour=16, minute=0)
        return start_date, end_date
    
    return end_date - timedelta(days=365*10), end_date

def fetch_historical_data(symbol, interval):
    """Add request debugging"""
    start_date, end_date = get_valid_date_range(interval)
    print(f"Fetching {symbol} from {start_date} to {end_date}")
    
    try:
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            timeout=30,
            threads=False  # Disable parallel requests
        )
        print(f"Raw data columns: {data.columns.tolist()}")
        return data
    except Exception as e:
        print(f"Critical error fetching {symbol}: {str(e)}")
        return pd.DataFrame()

def save_data(symbol, df, interval):
    """Add file write verification"""
    try:
        if df.empty:
            print(f"Skipping empty dataset for {symbol}")
            return
            
        folder_name = interval.replace('m', 'min').replace('h', 'hour')
        save_path = os.path.join(BASE_DATA_DIR, folder_name)
        
        print(f"Creating directory: {save_path}")
        os.makedirs(save_path, exist_ok=True)
        
        filename = f"{symbol}_{interval}_{df.index[0].date()}_to_{df.index[-1].date()}.csv"
        filepath = os.path.join(save_path, filename)
        
        print(f"Writing {len(df)} rows to {filepath}")
        df.to_csv(filepath)
        
        # Verify write
        if os.path.exists(filepath):
            print(f"Successfully saved {os.path.getsize(filepath)/1024:.1f} KB")
        else:
            print("File write failed!")
            
    except Exception as e:
        print(f"Save failed for {symbol}: {str(e)}")

def main():
    print("Starting enhanced data pipeline...")
    start_time = datetime.now()
    
    try:
        print(f"Base data directory: {BASE_DATA_DIR}")
        print(f"Python version: {os.sys.version}")
        print(f"yfinance version: {yf.__version__}")
        
        for idx, symbol in enumerate(SYMBOLS, 1):
            print(f"\nProcessing {idx}/{len(SYMBOLS)}: {symbol}")
            
            df = fetch_historical_data(symbol, INTERVAL)
            if not df.empty:
                save_data(symbol, df, INTERVAL)
            else:
                print(f"No data for {symbol}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nUser interrupted process")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        print(f"\nTotal runtime: {datetime.now() - start_time}")

if __name__ == "__main__":
    main()