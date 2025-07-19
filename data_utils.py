'''
This module contains functions for data processing 
such as prepare data for backtesting etc.
'''

import pandas as pd
import stock_utils



def quarterly_return(ticker: str, len_quarter: int = 2) -> pd.DataFrame:
    '''
    Calculate the quarterly return of a stock.
    6month_return = (R(Q3) - R(Q1)) / R(Q1)
    where R(Q1) is the return of the first quarter and R(Q3) is the return of the third quarter.
    '''
    # call compound_return of days+1 because we need two days to get one return
