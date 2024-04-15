"""Module to get market data prices."""

import yfinance as yf


def get_price(symbol):
    """
    Fetches the closing price of a financial instrument for the current day.

    Args:
    - symbol (str): Ticker symbol of the financial instrument.

    Returns:
    - float: Closing price of the financial instrument for the current day.
    """
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'].iloc[-1]
