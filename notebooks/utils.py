import os
import pandas as pd
from configs import EXT_DATA_DIR

# DEPRECATED!
def _get_prices(asset_type, adjustment, period, timeframe, ticker_symbol):
    CSV_DEST_DIR = os.path.join(
        EXT_DATA_DIR, asset_type, timeframe, "csv"
    )

    CSV_DEST_DIR = f"/media/reggie/reg_ext/frd-historical/data/stock/{timeframe}/csv/"

    
    print(f"Looking for {ticker_symbol} {asset_type} csv file in {CSV_DEST_DIR}")

    _adjustment = adjustment.replace("_", "")
    target_file = f"{ticker_symbol}_{period}_{timeframe}_{_adjustment}.txt"
    print(target_file)
    prices_df = None
    for file in os.listdir(CSV_DEST_DIR):
        if file == target_file:
            print(file)
            path = os.path.join(CSV_DEST_DIR, file)
            print(path)
            prices_df = pd.read_csv(path, sep=",", names=['date', 'open', 'high', 'low', 'close', 'volume'])

    if prices_df is None:
        print(f"Could not find {ticker_symbol} {asset_type} csv file in {CSV_DEST_DIR}")
        return None

    prices_df['date'] = pd.to_datetime(prices_df['date'])
    print(prices_df.shape)

    # Convert 'date' column to datetime if it's not already
    prices_df['date'] = pd.to_datetime(prices_df['date'])

    # Extract the day as YYYY-MM-DD
    prices_df['day'] = prices_df['date'].dt.date

    # Extract the time as HH:MM:SS
    prices_df['time'] = prices_df['date'].dt.time

    # Calculate the time ID (minute of the day from 1 to 1440)
    prices_df['time_id'] = prices_df['date'].dt.hour * 60 + prices_df['date'].dt.minute + 1

    # Show the DataFrame
    return prices_df

def get_prices(asset_type, adjustment, period, timeframe, ticker_symbol):
    # Example usage
    #asset_type = "stock"
    #adjustment = "adjsplitdiv"
    #period = "full"
    #timeframe = "1min"
    #ticker_symbol = "Z"
    #prices_df = get_prices(asset_type, adjustment, period, timeframe, ticker_symbol)
    #print(prices_df.shape)
    #prices_df

    CSV_DEST_DIR = os.path.join(
        EXT_DATA_DIR, asset_type, timeframe, "csv"
    )
    
    print(f"Looking for {ticker_symbol} {asset_type} csv file in {CSV_DEST_DIR}")

    _adjustment = adjustment.replace("_", "")
    target_file = f"{ticker_symbol}_{period}_{timeframe}_{_adjustment}.txt"
    print(target_file)
    
    prices_df = None
    for file in os.listdir(CSV_DEST_DIR):
        if file == target_file:
            print(file)
            path = os.path.join(CSV_DEST_DIR, file)
            break
    
    try:
        # Try reading the CSV file with robust error handling
        prices_df = pd.read_csv(
            path,
            sep=",",
            names=['date', 'open', 'high', 'low', 'close', 'volume'],
            header=0,  # Assuming the first row is a header, if not set to None
            on_bad_lines='warn',  # Skip bad lines
            engine='python'  # Use the Python engine for more flexible error handling
        )

    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

    prices_df['date'] = pd.to_datetime(prices_df['date'])
    print(prices_df.shape)

    # Convert 'date' column to datetime if it's not already
    prices_df['date'] = pd.to_datetime(prices_df['date'])

    # Extract the day as YYYY-MM-DD
    prices_df['day'] = prices_df['date'].dt.date

    # Extract the time as HH:MM:SS
    prices_df['time'] = prices_df['date'].dt.time

    # Calculate the time ID (minute of the day from 1 to 1440)
    prices_df['time_id'] = prices_df['date'].dt.hour * 60 + prices_df['date'].dt.minute + 1

    return prices_df


