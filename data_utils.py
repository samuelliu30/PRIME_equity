'''
This module contains functions for data processing 
such as prepare data for backtesting etc.
'''

import pandas as pd
import stock_utils
from datetime import datetime, timedelta
import os

def quarterly_return(ticker: str, len_quarter: int = 2) -> pd.DataFrame:
    '''
    Calculate the quarterly return of a stock.
    6month_return = (R(Q3) - R(Q1)) / R(Q1)
    where R(Q1) is the return of the first quarter and R(Q3) is the return of the third quarter.
    '''
    # call compound_return of days+1 because we need two days to get one return
    pass

def p_e_ratio(ticker: str) -> pd.DataFrame:
    '''
    Calculate the p/e ratio of a stock.
    '''
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{ticker}_pe_ratio_cache.csv")
    
    # Check if the cache file exists
    if os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file)
        except Exception as exc:
            stock_utils.logger.warning("Failed to read cache for %s: %s", ticker, exc)
    
    eps = stock_utils.get_stock_eps(ticker)
    pe_ratios = []

    for _, row in eps.iterrows():
        date = row['date']
        reported_eps = row['reportedEPS']
        
        # Fetch the stock price for the given date
        # Convert string to datetime
        target_date = datetime.strptime(date, "%Y-%m-%d")

        # Initialize stock object
        stock = stock_utils.yf.Ticker(ticker)

        # Check if the target_date is a trading day, try up to 3 previous days
        max_attempts = 3
        attempts = 0
        hist = stock.history(start=target_date, end=target_date + timedelta(days=1))
        while hist.empty and attempts < max_attempts:
            # If not a trading day, move to the previous day
            target_date -= timedelta(days=1)
            hist = stock.history(start=target_date, end=target_date + timedelta(days=1))
            attempts += 1
        
        if not hist.empty and reported_eps:
            # Get the closing price for the date
            price = hist['Close'].iloc[0]
            # Calculate the P/E ratio
            pe_ratio = price / reported_eps
            pe_ratios.append({'date': date, 'pe_ratio': pe_ratio})
        else:
            pe_ratios.append({'date': date, 'pe_ratio': None})

    df = pd.DataFrame(pe_ratios)
    
    # Save the DataFrame to a cache file
    df.to_csv(cache_file, index=False)
    
    return df

if __name__ == "__main__":
    print(p_e_ratio("NVDA"))