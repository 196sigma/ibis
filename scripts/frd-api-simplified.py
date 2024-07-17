from math import e
import os
import shutil
import zipfile
import pandas as pd
import ast
import argparse
import pyarrow as pa
import pyarrow.parquet as pq

# TODO: Move important parameters to YAML file
# TODO: Add logging

PROJECT_DIR = "/home/reggie/Dropbox/ibis/"
FRD_DATA_DIR = os.path.join(PROJECT_DIR, "data", "frd-historical")
PARQUET_DIR = os.path.join(FRD_DATA_DIR, "stock", "combined", "adj_splitdiv", "1min")
ZIP_FILES_DIR = "/media/reggie/reg_ext/frd-historical/data/stock/zips/"
asset_type = "stock"
timeframe = "1min"
adjustment = "adj_splitdiv"
period = "full"

#CSV_FILES_DIR = os.path.join(FRD_DATA_DIR, asset_type, "combined", adjustment, timeframe)

# read params from command line
args = argparse.ArgumentParser()
args.add_argument("--ticker", type=str, default="")
args.add_argument("--combine", type=ast.literal_eval, default=False)
args.add_argument("--convert", type=ast.literal_eval, default=False)
args.add_argument("--cleanup", type=ast.literal_eval, default=False)
args = args.parse_args()
ticker_first_letter = args.ticker
combine = args.combine
convert = args.convert
cleanup = args.cleanup
# print arguments received
print(f"ticker_first_letter: {ticker_first_letter}")
print(f"combine: {combine}")
print(f"convert: {convert}")
print(f"cleanup: {cleanup}")

zip_path = os.path.join(ZIP_FILES_DIR, adjustment, timeframe, f"{ticker_first_letter}_{adjustment}_{timeframe}.zip")
#csv_dest_path = os.path.join(CSV_FILES_DIR, f"{ticker_first_letter}_{adjustment}_{timeframe}.csv")
dest_dir = os.path.join(FRD_DATA_DIR, "tmp")

def extract_zip(src_path):
    """
    Extract individual .txt files (one for each ticker symbol) from the .zip file. 
    Store them in a temporary directory.
    
    Parameters
    ----------
    src_path : string
        Path to the .zip file to extract.
    
    Returns
    -------
    dest_dir : string
        Path to the directory where the .txt files were extracted.
    """
    # Empty the source directory for unzipped .txt data files if it already exists, create it otherwise
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
        print(f"Removed directory {dest_dir}")
    os.makedirs(dest_dir)
    print(f"Created directory {dest_dir}")
    print(f"Extracting {src_path} to {dest_dir}")
    with zipfile.ZipFile(src_path, 'r') as zip_ref:
        zip_ref.extractall(path=dest_dir)
    n_files = len(os.listdir(dest_dir))
    print(f"Extracted {n_files} files from {src_path}")
    return dest_dir

# extract individual txt files from the zip file
src_path = extract_zip(zip_path)
print(src_path)
asset_data_files = [os.path.join(src_path, f) for f in os.listdir(src_path)]
print(f"Number of files: {len(asset_data_files)} in {src_path}")

if convert is True:
    # convert each csv to parquet then combine into one big parquet file
    dtype={'ticker': str, 'date': str, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': float}
    schema = pa.schema([
        pa.field("ticker", pa.string()),
        pa.field("date", pa.string()),
        pa.field("open", pa.float64()),
        pa.field("high", pa.float64()),
        pa.field("low", pa.float64()),
        pa.field("close", pa.float64()),
        pa.field("volume", pa.float64())
    ])
    for i, file_path in enumerate(asset_data_files):
        parquet_file_path = file_path.replace(".csv", ".parquet")
        print(f"Processing file {i+1}/{len(asset_data_files)}: {file_path}")
        try:
            df = pd.read_csv(file_path, dtype=dtype)
            df.to_parquet(parquet_file_path, engine='pyarrow', compression='snappy')
            print(f"Converted {ticker_first_letter}_{adjustment}_{timeframe}.parquet")
        except Exception as e:
            print(f"Error converting {file_path}: {e}")
            # TODO: Add logging

if combine is True:
    # combine all parquet files into one big parquet file
    # NB: This is broken, no `append=True` parameter in `pq.write_table` method!
    for i, file_path in enumerate(asset_data_files):
        parquet_file_path = file_path.replace(".csv", ".parquet")
        combined_parquet_file = os.path.join(PARQUET_DIR, f"{ticker_first_letter}_{adjustment}_{timeframe}.parquet")
        print(f"Processing file {i+1}/{len(asset_data_files)}: {parquet_file_path}")
        table = pq.read_table(parquet_file_path)
        pq.write_table(table, parquet_file_path, append=True, compression='snappy')
        print(f"Appended {parquet_file_path} to {combined_parquet_file}")

if cleanup is True:
    # clean up: remove individual .txt files
    print(f"Removing {len(asset_data_files)} files from {src_path}")
    for file in asset_data_files:
        os.remove(file)
    # clean up: remove individual parquet files
    print(f"Removing {len(asset_data_files)} files from {src_path}")
    for file in asset_data_files:
        parquet_file_path = file.replace(".csv", ".parquet")
        os.remove(parquet_file_path)