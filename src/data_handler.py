import os
import pandas as pd
import queue
from datetime import datetime

# Robust import handling for direct script execution vs package module execution
try:
    from src.events import MarketEvent
except ImportError:
    from events import MarketEvent

class ParquetDataHandler:
    """
    ParquetDataHandler reads the cleaned price parquet file and 
    provides an interface to stream market data one timestamp (bar) at a time.
    """
    def __init__(self, events_queue: queue.Queue, parquet_path: str = "data/cleaned_prices.parquet"):
        self.events_queue = events_queue
        self.parquet_path = parquet_path
        
        if not os.path.exists(self.parquet_path):
            raise FileNotFoundError(f"Cleaned price file not found at '{self.parquet_path}'. Run 'python run_pipeline.py' first.")
        
        self.symbol_data = self._load_data()
        self.all_dates = self.symbol_data.index
        self.continue_backtest = True
        self.bar_index = 0

    def _load_data(self) -> pd.DataFrame:
        df = pd.read_parquet(self.parquet_path)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        print(f"DataHandler loaded {df.shape[1]} tickers across {len(df)} trading days.")
        return df

    def get_latest_bar(self, ticker: str) -> float:
        curr_idx = max(0, self.bar_index - 1)
        if ticker in self.symbol_data.columns:
            return self.symbol_data.loc[self.all_dates[curr_idx], ticker]
        raise KeyError(f"Ticker {ticker} not found in data handler.")

    def get_latest_bar_datetime(self) -> datetime:
        curr_idx = max(0, self.bar_index - 1)
        return self.all_dates[curr_idx]

    def get_latest_bars(self, N: int = 1) -> pd.DataFrame:
        curr_idx = max(0, self.bar_index - 1)
        start_idx = max(0, curr_idx - N + 1)
        return self.symbol_data.iloc[start_idx : curr_idx + 1]

    def update_market_data(self) -> bool:
        if self.bar_index < len(self.all_dates):
            self.bar_index += 1
            self.events_queue.put(MarketEvent())
            return True
        else:
            self.continue_backtest = False
            return False

if __name__ == "__main__":
    q = queue.Queue()
    handler = ParquetDataHandler(q)
    print(f"Starting simulation stream. Total bars: {len(handler.all_dates)}")
    for i in range(3):
        has_data = handler.update_market_data()
        if has_data:
            current_time = handler.get_latest_bar_datetime()
            event = q.get()
            print(f"Step {i+1} | Time: {current_time.strftime('%Y-%m-%d')} | Event: {event.type}")