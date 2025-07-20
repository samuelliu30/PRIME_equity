'''
This module contains functions for data processing 
such as prepare data for backtesting etc.
'''

import pandas as pd
import stock_utils
from datetime import datetime, timedelta
import os

def quarterly_return(ticker: str, start_date: datetime, days: int = 2) -> pd.DataFrame:
    '''
    Calculate the quarterly return of a stock.
    6month_return = (R(Q3) - R(Q1)) / R(Q1)
    where R(Q1) is the return of the first quarter and R(Q3) is the return of the third quarter.
    '''
    cache_dir = "cache/quarterly_return"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{ticker}_quarterly_return_{start_date.strftime('%Y%m%d')}_{days}_days_cache.csv")
    
    # Check if the cache file exists
    if os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        except Exception as exc:
            stock_utils.logger.warning("Failed to read cache for %s: %s", ticker, exc)
    
    # call compound_return of days+1 because we need two days to get one return
    returns = stock_utils.compound_return(ticker, days + 1, start_date)
    # Set the index of the DataFrame to the start_date
    returns.index = [start_date]
    
    # Save the returns to a cache file
    returns.to_csv(cache_file)
    
    return returns

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

def get_yoy_return(ticker: str) -> pd.DataFrame:
    '''
    Calculate the year-over-year return of a stock.
    '''
    revenue = stock_utils.get_stock_revenue(ticker)    
    # Ensure totalRevenue is numeric
    revenue['totalRevenue'] = pd.to_numeric(revenue['totalRevenue'], errors='coerce')

    # Calculate year-over-year return using the formula (new - old) / old
    revenue['yoy_return'] = revenue['totalRevenue'].pct_change(-1)
    
    # Drop the last row as it will have NaN for YoY return
    revenue_yoy = revenue.dropna(subset=['yoy_return'])
    
    return revenue_yoy[['date', 'yoy_return']]


def get_stock_eps(ticker: str) -> pd.DataFrame:
    '''
    Get the earnings per share of a stock.
    '''
    eps = stock_utils.get_stock_eps(ticker)
    return eps

if __name__ == "__main__":
    #print(p_e_ratio("NVDA"))
    #print(get_yoy_return("NVDA"))
    print(quarterly_return("NVDA", datetime(2024, 1, 1), 360))