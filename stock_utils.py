'''
This module contains functions for fetching data from Yahoo Finance API
'''

from __future__ import annotations

import logging
from typing import Optional

import yfinance as yf
import pandas as pd
import requests
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

load_dotenv()
alphavantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')


def get_pe_ratio(ticker: str, *, forward: bool = False, raise_on_missing: bool = False) -> Optional[float]:
    """Return the price-to-earnings ratio (P/E) for a stock ticker.

    Parameters
    ----------
    ticker : str
        The stock symbol, e.g. "AAPL".
    forward : bool, default False
        If *True*, return the forward P/E (based on estimated future earnings).
        If *False*, return the trailing P/E (based on the last 12 months of earnings).
    raise_on_missing : bool, default False
        If *True* and the requested P/E value is not available, raise a ``ValueError``.
        If *False*, simply return ``None`` when the ratio is unavailable.

    Returns
    -------
    Optional[float]
        The requested P/E ratio, or ``None`` if it could not be obtained and
        *raise_on_missing* is *False*.
    """

    if not ticker:
        raise ValueError("`ticker` must be a non-empty string")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info  # network call to Yahoo Finance API
    except Exception as exc:
        logger.warning("Failed to fetch data for %s: %s", ticker, exc)
        if raise_on_missing:
            raise
        return None

    key = "forwardPE" if forward else "trailingPE"
    pe_ratio = info.get(key)

    if pe_ratio is None and raise_on_missing:
        raise ValueError(f"P/E ratio ({key}) not available for ticker '{ticker}'.")

    return pe_ratio

def get_stock_eps(ticker: str) -> pd.DataFrame:
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{ticker}_eps_cache.csv")
    
    # Check if the cache file exists
    if os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file)
        except Exception as exc:
            logger.warning("Failed to read cache for %s: %s", ticker, exc)
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "EARNINGS",
            "symbol": ticker,
            "apikey": alphavantage_api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Extract the earnings data
        earnings = data.get("quarterlyEarnings", [])

        # Create a DataFrame with date and reportedEPS
        eps_data = [
            {"date": entry.get("fiscalDateEnding"), "reportedEPS": entry.get("reportedEPS")}
            for entry in earnings
        ]

        df = pd.DataFrame(eps_data)
        
        # Save the DataFrame to a cache file
        df.to_csv(cache_file, index=False)
        
        return df
    except Exception as exc:
        logger.warning("Failed to fetch earnings for %s: %s", ticker, exc)
        return pd.DataFrame()

if __name__ == "__main__":
    print(get_stock_eps("AAPL"))