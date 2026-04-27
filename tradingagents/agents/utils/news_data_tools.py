from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config
from tradingagents.anonymization.ticker_map import deanonymize_ticker, scrub_ticker_text
from tradingagents.anonymization.noun_scrubber import scrub_news_text

@tool
def get_news(
    ticker: Annotated[str, "Ticker symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve news data for a given ticker symbol.
    Uses the configured news_data vendor.
    Args:
        ticker (str): Ticker symbol
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted string containing news data
    """
    cfg = get_config()
    real = deanonymize_ticker(ticker, cfg)
    out = route_to_vendor("get_news", real, start_date, end_date)
    out = scrub_news_text(out, cfg)
    out = scrub_ticker_text(out, cfg)
    return out

@tool
def get_global_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    limit: Annotated[int, "Maximum number of articles to return"] = 5,
) -> str:
    """
    Retrieve global news data.
    Uses the configured news_data vendor.
    Args:
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days to look back (default 7)
        limit (int): Maximum number of articles to return (default 5)
    Returns:
        str: A formatted string containing global news data
    """
    cfg = get_config()
    out = route_to_vendor("get_global_news", curr_date, look_back_days, limit)
    out = scrub_news_text(out, cfg)
    out = scrub_ticker_text(out, cfg)
    return out

@tool
def get_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
) -> str:
    """
    Retrieve insider transaction information about a company.
    Uses the configured news_data vendor.
    Args:
        ticker (str): Ticker symbol of the company
    Returns:
        str: A report of insider transaction data
    """
    cfg = get_config()
    real = deanonymize_ticker(ticker, cfg)
    out = route_to_vendor("get_insider_transactions", real)
    out = scrub_ticker_text(out, cfg)
    return out
