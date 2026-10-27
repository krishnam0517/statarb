# Statistical Arbitrage Platform

A modular Python-based statistical arbitrage research platform built on WSL2 (Ubuntu), utilizing `yfinance`, `pandas`, `DuckDB`, and Parquet for efficient data engineering and pair-selection analytics.

## Project Architecture
- `src/download_data.py`: Ingests historical multi-index price data.
- `src/get_sectors.py`: Maps tickers to their respective GICS sectors and industries.
- `src/cleaning.py`: Filters out illiquid assets and short-history tickers, forward-fills gaps, and outputs cleaned Parquet storage.
- `src/data_report.py`: Validates data health and missing value distributions.

## Quickstart / Pipeline Rebuild
To rebuild the entire cleaned dataset from scratch with a single command: