import json
import os
import time
import yfinance as yf

def get_stock_sectors(tickers: list, output_path: str = "data/stock_sectors.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    abs_path = os.path.abspath(output_path)
    print(f"Target file absolute path: {abs_path}")
    
    sector_mapping = {}
    
    # Load existing if any
    if os.path.exists(output_path):
        try:
            with open(output_path, "r") as f:
                sector_mapping = json.load(f)
        except:
            pass

    print(f"Fetching sector information for {len(tickers)} tickers...")
    
    for i, ticker in enumerate(tickers, 1):
        if ticker in sector_mapping and sector_mapping[ticker]["sector"] != "Unknown":
            print(f"[{i}/{len(tickers)}] Skipping {ticker} (already cached)")
            continue
            
        try:
            print(f"[{i}/{len(tickers)}] Fetching {ticker}...")
            t = yf.Ticker(ticker)
            info = t.info
            sector = info.get("sector", "Unknown")
            industry = info.get("industry", "Unknown")
            sector_mapping[ticker] = {
                "sector": sector,
                "industry": industry
            }
            
            # Save incrementally after each ticker
            with open(output_path, "w") as f:
                json.dump(sector_mapping, f, indent=4)
                
            time.sleep(0.2)
        except Exception as e:
            print(f"Could not fetch info for {ticker}: {e}")
            sector_mapping[ticker] = {"sector": "Unknown", "industry": "Unknown"}
    
    print(f"Successfully saved sector labels to {abs_path}")
    return sector_mapping

if __name__ == "__main__":
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM", "V", "JNJ",
        "UNH", "XOM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO",
        "BAC", "COST", "TMO", "WMT", "MCD", "CSCO", "ACN", "ABT", "LIN", "DHR",
        "PFE", "ADBE", "NFLX", "AMD", "NKE", "TXN", "PM", "ORCL", "DIS", "INTC",
        "QCOM", "IBM", "CAT", "GE", "SPGI", "AXP", "AMGN", "UPS", "HON", "BA"
    ]
    get_stock_sectors(tickers)