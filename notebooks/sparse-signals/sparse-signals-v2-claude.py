import warnings
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LassoCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from statsmodels.tsa.ar_model import AutoReg
import pickle

# Suppress warnings
warnings.filterwarnings('ignore')

# Constants
START_YEAR = 2017
END_YEAR = 2017
ASSET_TYPE = 'stock'
PERIOD = '1min'
TIMEFRAME = 'full'
ADJUSTMENT = 'adjsplitdiv'
N_TICKERS = 300
FOCAL_TICKER = 'AAPL'
WINDOW_SIZE = 30
PREDICTION_HORIZON = 1

# Helper functions
def get_csv_dir():
    return "E:/frd-historical/data/{}/{}/csv/" if os.name == 'nt' else "/media/reggie/reg_ext/frd-historical/data/{}/{}/csv/"

def add_trading_hours(df):
    df['time'] = df.index.strftime('%H%M').astype(int)
    df['is_trading_hour'] = (df['time'] >= 930) & (df['time'] <= 1600)
    return df

def load_data(csv_dir, tickers, start_year, end_year):
    data = {}
    dtype = {'date': str, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': float}
    columns = list(dtype.keys())
    
    for ticker in tqdm(tickers):
        csv_path = os.path.join(csv_dir, f"{ticker}_{TIMEFRAME}_{PERIOD}_{ADJUSTMENT}.txt")
        _columns = columns.copy()
        _columns[1:] = [f"{ticker}_{col}" for col in _columns[1:]]
        
        df = pd.read_csv(csv_path, names=_columns)
        df['date'] = pd.to_datetime(df['date'])
        df = df[['date', f'{ticker}_close']].set_index("date")
        
        df = df[(df.index >= pd.to_datetime(f"{start_year}-01-01")) & 
                (df.index <= pd.to_datetime(f"{end_year}-12-31 23:59:59"))]
        
        if not df.empty:
            data[ticker] = df
    
    return data

def preprocess_data(data, nsamples=10_000, trading_hours=True):
    for ticker, df in data.items():
        df = df.asfreq('1T').fillna(method='ffill')
        if nsamples > -1:
            df = df.iloc[:nsamples]
        if trading_hours:
            df = add_trading_hours(df)
            df = df[df['is_trading_hour']]
        data[ticker] = df
    return data

def calculate_lagged_returns(data, lags=3):
    for ticker, df in data.items():
        df[f'{ticker}_return'] = df[f'{ticker}_close'].pct_change()
        for i in range(1, lags + 1):
            df[f'{ticker}_lag_{i}_return'] = df[f'{ticker}_close'].shift(1).pct_change(periods=i)
        data[ticker] = df
    return data

def merge_features(data, focal_ticker):
    x = data[focal_ticker].drop(columns=[f'{focal_ticker}_close', 'is_trading_hour', 'time'])
    n = len(x)
    
    for ticker, df in data.items():
        if ticker != focal_ticker:
            y = df.drop(columns=[f'{ticker}_close', 'is_trading_hour', 'time'])
            if y.shape[0] >= n:
                x = x.merge(y, left_index=True, right_index=True, how='left')
    
    return x.iloc[4:]

def rolling_window_predictions(data, focal_ticker, window_size, prediction_horizon):
    focal_columns = [f'{focal_ticker}_return'] + [f'{focal_ticker}_lag_{i}_return' for i in range(1, 4)]
    lagged_columns = [f'{ticker}_lag_{i}_return' for ticker in set([col.split("_")[0] for col in data.columns]) for i in range(1, 4)]
    
    results = {'date': [], 'lasso': [], 'ar': [], 'ret': []}
    
    for i in tqdm(range(window_size, len(data) - prediction_horizon)):
        start_idx, end_idx = i - window_size, i
        
        X = data[lagged_columns].iloc[start_idx:end_idx].values
        y = data[f'{focal_ticker}_return'].iloc[start_idx:end_idx].values
        
        if len(X) < 5 or len(y) < 5:
            continue
        
        lasso = LassoCV(cv=5).fit(X, y)
        latest_data = data[lagged_columns].iloc[end_idx:end_idx+1].dropna()
        if latest_data.empty:
            continue
        lasso_pred = lasso.predict(latest_data)[0]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ar_model = AutoReg(data[f'{focal_ticker}_return'].iloc[start_idx:end_idx].dropna(), lags=10).fit()
            ar_pred = float(ar_model.predict(start=len(ar_model.model.endog), end=len(ar_model.model.endog)))
        
        results['date'].append(data.index[end_idx + prediction_horizon])
        results['lasso'].append(lasso_pred)
        results['ar'].append(ar_pred)
        results['ret'].append(y[-1])
    
    return pd.DataFrame(results).set_index('date')

# Main execution
if __name__ == "__main__":
    csv_dir = get_csv_dir().format(ASSET_TYPE, PERIOD)
    tickers = [f.split("_")[0] for f in os.listdir(csv_dir) if f.endswith(".txt")][:N_TICKERS]
    
    data = load_data(csv_dir, tickers, START_YEAR, END_YEAR)
    data = preprocess_data(data)
    data = calculate_lagged_returns(data)
    
    return_features_df = merge_features(data, FOCAL_TICKER)
    
    # Remove columns with missing values
    return_features_df = return_features_df.dropna(axis=1)
    
    with open('return_features_df.pickle', 'wb') as f:
        pickle.dump(return_features_df, f)
    
    results_df = rolling_window_predictions(return_features_df, FOCAL_TICKER, WINDOW_SIZE, PREDICTION_HORIZON)
    
    print(results_df.shape)
    print(results_df.info())
    
    with open('results_df.pickle', 'wb') as f:
        pickle.dump(results_df, f)