import os
import yfinance as yf
import pandas as pd

def download_historical_prices(tickers: list, years: int = 10, output_path: str = "data/sp500_prices.parquet"):
    print(f"Downloading historical data for {len(tickers)} tickers ({years} years)...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Download using yfinance with threading enabled for speed
    df = yf.download(
        tickers, 
        period=f"{years}y", 
        group_by='ticker', 
        auto_adjust=True, 
        threads=True
    )
    
    if df.empty:
        raise ValueError("Downloaded dataframe is empty. Check ticker symbols or network connection.")
        
    df.to_parquet(output_path)
    print(f"Successfully saved raw prices to {output_path} with shape: {df.shape}")
    return df

if __name__ == "__main__":
    target_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM", "V", "JNJ",
        "UNH", "XOM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO",
        "BAC", "COST", "TMO", "WMT", "MCD", "CSCO", "ACN", "ABT", "LIN", "DHR",
        "PFE", "ADBE", "NFLX", "AMD", "NKE", "TXN", "PM", "ORCL", "DIS", "INTC",
        "QCOM", "IBM", "CAT", "GE", "SPGI", "AXP", "AMGN", "UPS", "HON", "BA"
    ]
    download_historical_prices(target_tickers)