# supress statsmodels warnings
import warnings
warnings.filterwarnings('ignore')

import os
import pickle
from joblib import Parallel, delayed
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from statsmodels.tsa.ar_model import AutoReg
from tqdm import tqdm
from IPython.display import display

_start_year = 2017
_end_year = 2017
start_year = pd.to_datetime(f"{_start_year}-01-01 00:00:00")
end_year = pd.to_datetime(f"{_end_year}-12-31 23:59:59")

N_TICKERS = 300
focal_ticker = 'AAPL'
asset_type = 'stock'
period = '1min'
timeframe = 'full'
adjustment = 'adjsplitdiv'
window_size = 30
prediction_horizon = 1

with open('return_features_df.pickle', 'rb') as file:
    return_features_df = pickle.load(file)
print(return_features_df.shape)
print(return_features_df.info())

tickers = list(set([col.split("_")[0] for col in return_features_df.columns]))
len(tickers)
print(f"Number of tickers: {len(tickers)}")

data = return_features_df.copy()
#data = data.iloc[:32]

#def rolling_window_predictions(data, focal_ticker, window_size=30, prediction_horizon=1):
# Identify columns for the focal ticker
focal_columns = [f'{focal_ticker}_return', 
                    f'{focal_ticker}_lag_1_return', 
                    f'{focal_ticker}_lag_2_return', 
                    f'{focal_ticker}_lag_3_return']

# Prepare the list of all lagged columns
#lagged_columns = [col for col in data.columns if 'lag' in col]
lagged_columns = []
for ticker in tickers:
    for i in range(1, 4):
        lagged_columns.append(f'{ticker}_lag_{i}_return')
results = {'date': [], 'lasso': [], 'ar': [], 'ret': []}

n_windows = len(data) - window_size - prediction_horizon

for i in tqdm(range(window_size, len(data) - prediction_horizon)):
    start_idx = i - window_size
    end_idx = i

    # Prepare predictors (X) and response (y)
    _X = data[lagged_columns].iloc[start_idx:end_idx]
    _y = data[f'{focal_ticker}_return'].iloc[start_idx:end_idx]
    print(f"start_idx: {start_idx}, end_idx: {end_idx}, X dim: {_X.shape}, y dim: {_y.shape}")
    if len(_X) < 5 or len(_y) < 5:  # Ensure there are enough samples for cross-validation
        continue
    
    X = _X.values
    y = _y.values

    # LASSO Model
    lasso = LassoCV(cv=10).fit(X, y)
    latest_data = data[lagged_columns].iloc[end_idx:end_idx+1].dropna()
    if latest_data.empty:
        continue
    lasso_pred = lasso.predict(latest_data)[0]
    
    # AR Model
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ar_model = AutoReg(data[f'{focal_ticker}_return'].iloc[start_idx:end_idx].dropna(), lags=10).fit()
        #ar_pred = ar_model.predict(start=len(ar_model.model.endog), end=len(ar_model.model.endog))[0]
        ar_pred = float(ar_model.predict(start=len(ar_model.model.endog), end=len(ar_model.model.endog)))

    # Store predictions
    results['date'].append(data.index[end_idx + prediction_horizon])
    results['lasso'].append(lasso_pred)
    results['ar'].append(ar_pred)
    results['ret'].append(y[-1])

    #return results

#results = rolling_window_predictions(return_features_df, focal_ticker)

# Convert results to DataFrame for easier analysis
results_df = pd.DataFrame(results)
results_df.set_index('date', inplace=True)
results_df

print(results_df.shape)
print(results_df.info())

with open('results_df.pickle', 'wb') as f:
    pickle.dump(results_df, f)