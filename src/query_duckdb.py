import duckdb

def analyze_prices_with_duckdb(parquet_path: str = "data/cleaned_prices.parquet"):
    con = duckdb.connect()
    
    print("=== 1. Dataset Date Range & Row Count ===")
    summary_query = f"""
        SELECT 
            MIN(Date) AS start_date,
            MAX(Date) AS end_date,
            COUNT(*) AS total_trading_days
        FROM read_parquet('{parquet_path}')
    """
    summary_df = con.execute(summary_query).df()
    print(summary_df)
    
    print("\n=== 2. Sample Schema Columns ===")
    schema_df = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}')").df()
    print(schema_df.head(10))
    
    con.close()

if __name__ == "__main__":
    analyze_prices_with_duckdb()