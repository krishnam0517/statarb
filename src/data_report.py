import pandas as pd
import numpy as np

def generate_quality_report(
    raw_path: str = "data/sp500_prices.parquet",
    cleaned_path: str = "data/cleaned_prices.parquet"
):
    print("==========================================")
    print("          DATA QUALITY REPORT             ")
    print("==========================================")

    # 1. Load data
    raw_df = pd.read_parquet(raw_path)
    cleaned_df = pd.read_parquet(cleaned_path)

    # Handle raw multi-index if needed to get raw tickers
    if isinstance(raw_df.columns, pd.MultiIndex):
        raw_close = raw_df.xs('Close', level=1, axis=1)
    else:
        raw_close = raw_df

    raw_tickers = set(raw_close.columns)
    cleaned_tickers = set(cleaned_df.columns)
    dropped_tickers = raw_tickers - cleaned_tickers

    # 2. Universe Size
    print(f"\n[Universe Summary]")
    print(f"• Initial Tickers Count: {len(raw_tickers)}")
    print(f"• Cleaned Tickers Count: {len(cleaned_tickers)}")
    print(f"• Tickers Dropped:       {len(dropped_tickers)}")
    if dropped_tickers:
        print(f"  -> Dropped List: {sorted(list(dropped_tickers))}")

    # 3. Missing Values Analysis (Raw Data)
    print(f"\n[Missing Values & History (Raw Data)]")
    missing_counts = raw_close.isnull().sum()
    missing_pcts = (missing_counts / len(raw_close)) * 100
    
    summary_missing = pd.DataFrame({
        'Missing Days': missing_counts,
        'Missing %': missing_pcts
    }).sort_values(by='Missing %', ascending=False)

    print("Top 5 tickers with highest missing data in raw set:")
    print(summary_missing.head(5).to_string())

    # Overall missing percentage across entire raw matrix
    total_cells = raw_close.size
    total_missing = raw_close.isnull().sum().sum()
    overall_missing_pct = (total_missing / total_cells) * 100
    print(f"\n• Overall Dataset Missing Data: {overall_missing_pct:.2f}%")
    print(f"• Total Trading Days (Rows):   {len(cleaned_df)}")
    print(f"• Date Range:                  {cleaned_df.index.min().strftime('%Y-%m-%d')} to {cleaned_df.index.max().strftime('%Y-%m-%d')}")
    print("\n==========================================")
    print("Data Quality Verification Complete.")
    print("==========================================")

if __name__ == "__main__":
    generate_quality_report()