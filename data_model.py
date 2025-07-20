import pandas as pd
import numpy as np
import data_utils
from datetime import datetime
import json

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
        ticker_dataframes[ticker] = merged_data
    return ticker_dataframes

def compose_stock_data_by_date() -> pd.DataFrame:
    def format_quarter(date):
        month = date.month
        year = date.year
        if month in [1, 2, 3]:
            quarter = 1
        elif month in [4, 5, 6]:
            quarter = 2
        elif month in [7, 8, 9]:
            quarter = 3
        else:
            quarter = 4
        return f"{year}_q{quarter}"

    date_dict = {}

    for ticker in stock_list:
        merged_data = merge_indicator_data(ticker)
        merged_data['date'] = merged_data['date'].apply(format_quarter)

        for _, row in merged_data.iterrows():
            date = row['date']
            if date not in date_dict:
                date_dict[date] = {}
            date_dict[date][ticker] = {k: v for k, v in row.to_dict().items() if k not in ['ticker', 'date']}

    # Save the date_dict to a JSON file
    with open('stock_data_by_date.json', 'w') as json_file:
        json.dump(date_dict, json_file, indent=4)
    return date_dict
    

if __name__ == "__main__":
    print(compose_stock_data_by_date())