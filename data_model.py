import pandas as pd
import numpy as np
import data_utils
from datetime import datetime

stock_list = ["NVDA", "META", "AMD"]

def merge_indicator_data(ticker: str) -> pd.DataFrame:
    '''
    Merge the indicator data for a given ticker.
    '''
    eps = data_utils.get_stock_eps(ticker)
    pe_ratio = data_utils.p_e_ratio(ticker)
    yoy_return = data_utils.get_yoy_return(ticker)
    quarterly_returns = []

    for index, row in eps.iterrows():
        date = datetime.strptime(row['date'], "%Y-%m-%d")
        quarterly_return_six_month = data_utils.quarterly_return(ticker, date, 180)
        quarterly_return_one_year = data_utils.quarterly_return(ticker, date, 360)
        
        quarterly_returns.append({
            'date': row['date'],
            'quarterly_return_six_month': quarterly_return_six_month.iloc[0, 0],
            'quarterly_return_one_year': quarterly_return_one_year.iloc[0, 0]
        })

    quarterly_returns_df = pd.DataFrame(quarterly_returns)

    # Merge the dataframes
    merged_data = pd.merge(eps, pe_ratio, on='date', how='left')
    merged_data = pd.merge(merged_data, quarterly_returns_df, on='date', how='left')
    # Convert 'date' column to datetime for proper merging
    merged_data['date'] = pd.to_datetime(merged_data['date'])

    # Extract the year from the 'date' column
    merged_data['year'] = merged_data['date'].dt.year

    # Prepare the yoy_return data
    yoy_return['date'] = pd.to_datetime(yoy_return['date'])
    yoy_return['year'] = yoy_return['date'].dt.year

    # Merge the yoy_return data with the merged_data based on the year
    merged_data = pd.merge(merged_data, yoy_return[['year', 'yoy_return']], on='year', how='left')

    # Drop the 'year' column as it's no longer needed
    merged_data.drop(columns=['year'], inplace=True)

    
    return merged_data

if __name__ == "__main__":
    print(merge_indicator_data("NVDA").head(10))