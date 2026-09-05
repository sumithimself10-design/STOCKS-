"""
Starter universe of NSE-listed companies. This is intentionally a small,
well-known set (Nifty-heavy) rather than trying to ingest all ~2,000 NSE
listings on day one — get the pipeline correct against 30 liquid, well-
covered stocks before scaling ticker count up.

Add more by appending here and re-running `python -m app.scripts.seed_stocks`.
"""

NSE_UNIVERSE = [
    {"ticker": "RELIANCE", "name": "Reliance Industries", "sector": "Energy"},
    {"ticker": "TCS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"ticker": "HDFCBANK", "name": "HDFC Bank", "sector": "Financials"},
    {"ticker": "INFY", "name": "Infosys", "sector": "IT"},
    {"ticker": "ICICIBANK", "name": "ICICI Bank", "sector": "Financials"},
    {"ticker": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"ticker": "ITC", "name": "ITC", "sector": "FMCG"},
    {"ticker": "SBIN", "name": "State Bank of India", "sector": "Financials"},
    {"ticker": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom"},
    {"ticker": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Financials"},
    {"ticker": "LT", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"ticker": "AXISBANK", "name": "Axis Bank", "sector": "Financials"},
    {"ticker": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financials"},
    {"ticker": "ASIANPAINT", "name": "Asian Paints", "sector": "Consumer Durables"},
    {"ticker": "MARUTI", "name": "Maruti Suzuki", "sector": "Automobile"},
    {"ticker": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Pharma"},
    {"ticker": "TITAN", "name": "Titan Company", "sector": "Consumer Durables"},
    {"ticker": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Cement"},
    {"ticker": "WIPRO", "name": "Wipro", "sector": "IT"},
    {"ticker": "NESTLEIND", "name": "Nestle India", "sector": "FMCG"},
    {"ticker": "TATAMOTORS", "name": "Tata Motors", "sector": "Automobile"},
    {"ticker": "TATASTEEL", "name": "Tata Steel", "sector": "Metals"},
    {"ticker": "POWERGRID", "name": "Power Grid Corporation", "sector": "Utilities"},
    {"ticker": "NTPC", "name": "NTPC", "sector": "Utilities"},
    {"ticker": "ONGC", "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"ticker": "HCLTECH", "name": "HCL Technologies", "sector": "IT"},
    {"ticker": "JSWSTEEL", "name": "JSW Steel", "sector": "Metals"},
    {"ticker": "M&M", "name": "Mahindra & Mahindra", "sector": "Automobile"},
    {"ticker": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financials"},
    {"ticker": "ADANIENT", "name": "Adani Enterprises", "sector": "Conglomerate"},
]
