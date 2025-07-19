'''
This module contains functions for fetching data from Yahoo Finance API
'''

from __future__ import annotations

import logging
from typing import Optional

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


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


def get_historical_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetch historical market data for a given stock ticker within a specified date range.

    Parameters
    ----------
    ticker : str
        The stock symbol, e.g. "AAPL".
    start : str
        The start date for the historical data in the format 'YYYY-MM-DD'.
    end : str
        The end date for the historical data in the format 'YYYY-MM-DD'.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the historical market data, including columns like
        'Open', 'High', 'Low', 'Close', 'Volume', and 'Adj Close'.
    """
    if not ticker:
        raise ValueError("`ticker` must be a non-empty string")
    if not start or not end:
        raise ValueError("`start` and `end` must be non-empty strings in 'YYYY-MM-DD' format")

    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(start=start, end=end)
    except Exception as exc:
        logger.warning("Failed to fetch historical data for %s: %s", ticker, exc)
        return pd.DataFrame()  # Return an empty DataFrame on failure

    return hist_data

if __name__ == "__main__":
    print(get_pe_ratio("AAPL"))