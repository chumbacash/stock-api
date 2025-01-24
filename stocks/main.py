import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Configuration
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
BASE_DATA_DIR = './data'
PERIOD = '5y'  # Time range
INTERVAL = '4h'  # Data frequency

def create_data_directory(base_path: str, interval: str) -> str:
    """Create organized directory structure for data storage"""
    path = os.path.join(base_path, interval.replace('/', '-'))
    os.makedirs(path, exist_ok=True)
    return path

def fetch_stock_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch historical stock data with error handling"""
    try:
        return yf.Ticker(symbol).history(period=period, interval=interval)
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return pd.DataFrame()

def save_stock_data(symbol: str, data: pd.DataFrame, base_dir: str, 
                    period: str, interval: str) -> str:
    """Save data with organized structure and meaningful filename"""
    if data.empty:
        return ""
        
    # Create appropriate directory
    target_dir = create_data_directory(base_dir, interval)
    
    # Generate filename with metadata
    filename = f"{symbol}_{period}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = os.path.join(target_dir, filename)
    
    # Save data with metadata
    data.to_csv(filepath)
    return filepath

def main():
    print(f"Starting data pipeline for {len(SYMBOLS)} symbols...")
    start_time = datetime.now()
    
    for symbol in SYMBOLS:
        print(f"\nProcessing {symbol}:")
        print(f"Fetching {PERIOD} data at {INTERVAL} interval...")
        
        # Fetch data
        df = fetch_stock_data(symbol, PERIOD, INTERVAL)
        
        if not df.empty:
            # Save data
            filepath = save_stock_data(symbol, df, BASE_DATA_DIR, PERIOD, INTERVAL)
            print(f"Saved {len(df)} records to {filepath}")
            
            # Show sample data
            print(f"Latest data point: {df.index[-1].strftime('%Y-%m-%d')}")
        else:
            print(f"No data available for {symbol}")
    
    print(f"\nPipeline completed in {datetime.now() - start_time}")

if __name__ == "__main__":
    main()