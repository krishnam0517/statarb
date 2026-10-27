import os
import json
import pandas as pd

def load_prices(filepath: str = "data/sp500_prices.parquet") -> pd.DataFrame:
    """Load raw price data from parquet."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Price file not found at {filepath}. Run download_data.py first.")
    
    df = pd.read_parquet(filepath)
    print(f"Loaded price data with shape: {df.shape}")
    return df

def load_sectors(filepath: str = "data/stock_sectors.json") -> dict:
    """Load sector mapping JSON."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sector file not found at {filepath}. Run get_sectors.py first.")
    
    with open(filepath, "r") as f:
        sectors = json.load(f)
    print(f"Loaded sector mappings for {len(sectors)} tickers.")
    return sectors

if __name__ == "__main__":
    prices = load_prices()
    sectors = load_sectors()