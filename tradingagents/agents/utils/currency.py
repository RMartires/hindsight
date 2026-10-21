"""Denomination for NSE and Zerodha paper trading.

Prices, cash, fees, and proposed trades are rupees. OpenRouter token
estimates stay in USD and do not use this text.
"""

INR_AMOUNTS_CLAUSE = (
    "All prices, cash balances, fees, and transaction amounts are in INR "
    "(Indian rupees), from NSE/Zerodha data. Write amounts as INR. "
    "Do not use USD or the $ symbol."
)
