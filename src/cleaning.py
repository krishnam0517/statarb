import pandas as pd
import numpy as np

def clean_price_data(
    df_prices: pd.DataFrame, 
    min_history_ratio: float = 0.8
) -> pd.DataFrame:
    """
    Cleans raw multi-index price data where level 0 is Ticker and level 1 is Price attribute.
    """
    if isinstance(df_prices.columns, pd.MultiIndex):
        # Level 0 is Ticker, Level 1 is Price ('Open', 'High', 'Low', 'Close', 'Volume')
        prices = df_prices.xs('Close', level=1, axis=1)
    else:
        prices = df_prices

    print(f"Initial universe size: {prices.shape[1]} tickers, {prices.shape[0]} trading days.")

    # 1. Drop tickers with too many NaN values (insufficient history)
    valid_threshold = int(len(prices) * min_history_ratio)
    prices = prices.dropna(axis=1, thresh=valid_threshold)
    print(f"After filtering short history: {prices.shape[1]} tickers remaining.")

    # 2. Handle missing data via forward fill
    prices = prices.ffill(limit=3).bfill()

    # 3. Outlier check
    returns = prices.pct_change()
    extreme_moves = (returns.abs() > 0.5).sum()
    bad_tickers = extreme_moves[extreme_moves > 2].index
    if len(bad_tickers) > 0:
        print(f"Dropping tickers with extreme unexplained price jumps: {list(bad_tickers)}")
        prices = prices.drop(columns=bad_tickers)

    print(f"Final cleaned universe size: {prices.shape[1]} tickers.")
    return prices

if __name__ == "__main__":
    from loaders import load_prices
    raw_data = load_prices()
    cleaned_prices = clean_price_data(raw_data)
    
    cleaned_prices.to_parquet("data/cleaned_prices.parquet")
    print("Successfully saved cleaned prices to data/cleaned_prices.parquet")