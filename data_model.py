import pandas as pd
import numpy as np
import data_utils
from datetime import datetime

stock_list = ["NVDA", "AMD", "AVGO", "MRVL", "ADSK", "QCOM", "MU", "ASML"]

def merge_indicator_data(ticker: str) -> pd.DataFrame:
    '''
    Merge the indicator data for a given ticker.
    '''
    eps = data_utils.get_stock_eps(ticker)
    pe_ratio = data_utils.p_e_ratio(ticker)
    yoy_return = data_utils.get_yoy_return(ticker)
    quarterly_returns = []

    for index, row in eps.iterrows():
        date = row['date'] if isinstance(row['date'], datetime) else datetime.strptime(row['date'], "%Y-%m-%d")
        quarterly_return_six_month = data_utils.quarterly_return(ticker, date, 180)
        quarterly_return_one_year = data_utils.quarterly_return(ticker, date, 360)
        
        quarterly_returns.append({
            'date': row['date'],
            'quarterly_return_six_month': quarterly_return_six_month.iloc[0, 0],
            'quarterly_return_one_year': quarterly_return_one_year.iloc[0, 0]
        })

    quarterly_returns_df = pd.DataFrame(quarterly_returns)

    # Merge the dataframes
    # Ensure 'date' columns are of datetime type for both DataFrames
    eps['date'] = pd.to_datetime(eps['date'])
    pe_ratio['date'] = pd.to_datetime(pe_ratio['date'])
    quarterly_returns_df['date'] = pd.to_datetime(quarterly_returns_df['date'])

    merged_data = pd.merge(eps, pe_ratio, on='date', how='left')
    merged_data = pd.merge(merged_data, quarterly_returns_df, on='date', how='left')
    # Convert 'date' column to datetime for proper merging
    merged_data['date'] = pd.to_datetime(merged_data['date'])

    # Prepare the yoy_return data
    yoy_return['date'] = pd.to_datetime(yoy_return['date'])

    
    # Set the date as index for both dataframes to enable proper merging
    yoy_return_indexed = yoy_return.set_index('date')
    merged_data_indexed = merged_data.set_index('date')
    
    # Sort both dataframes in ascending order (oldest to newest) as required by merge_asof
    yoy_return_indexed = yoy_return_indexed.sort_index()
    merged_data_indexed = merged_data_indexed.sort_index()
    
    # Use merge_asof to get the last recorded yoy_return for each quarterly data point
    # This will use the last available yoy_return that is <= the quarterly date
    merged_data_indexed = pd.merge_asof(
        merged_data_indexed, 
        yoy_return_indexed[['yoy_return']], 
        left_index=True, 
        right_index=True, 
        direction='backward'
    )
    
    # Reset the index to get the date column back
    merged_data = merged_data_indexed.reset_index()
    merged_data.dropna(inplace=True)
    return merged_data

def compose_stock_data() -> pd.DataFrame:
    ticker_dataframes = {}
    for ticker in stock_list:
        merged_data = merge_indicator_data(ticker)
        print(ticker)
        print(merged_data)
        ticker_dataframes[ticker] = merged_data
    return ticker_dataframes


if __name__ == "__main__":
    compose_stock_data()