from abc import ABC, abstractmethod
import queue
import pandas as pd
import numpy as np

try:
    from src.events import SignalEvent
except ImportError:
    from events import SignalEvent


class Strategy(ABC):
    def __init__(self, data_handler, events_queue: queue.Queue):
        self.data_handler = data_handler
        self.events_queue = events_queue

    @abstractmethod
    def compute_signals(self, event) -> None:
        raise NotImplementedError("Strategy subclasses must implement compute_signals.")


class BuyAndHoldStrategy(Strategy):
    def __init__(self, data_handler, events_queue: queue.Queue, ticker: str = None):
        super().__init__(data_handler, events_queue)
        self.ticker = ticker if ticker else list(self.data_handler.symbol_data.columns)[0]
        self.invested = False

    def compute_signals(self, event) -> None:
        if not self.invested:
            current_time = self.data_handler.get_latest_bar_datetime()
            signal = SignalEvent(current_time, self.ticker, 'LONG', strength=1.0)
            self.events_queue.put(signal)
            self.invested = True


class PairsTradingStrategy(Strategy):
    """
    Statistical Arbitrage Pairs Trading Strategy using rolling Z-Score on a price spread.
    """
    def __init__(
        self, 
        data_handler, 
        events_queue: queue.Queue, 
        ticker_a: str = 'KO', 
        ticker_b: str = 'PEP', 
        window: int = 60, 
        entry_z: float = 2.0, 
        exit_z: float = 0.5
    ):
        super().__init__(data_handler, events_queue)
        self.ticker_a = ticker_a
        self.ticker_b = ticker_b
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z
        
        available = list(self.data_handler.symbol_data.columns)
        if self.ticker_a not in available or self.ticker_b not in available:
            if len(available) >= 2:
                self.ticker_a = available[0]
                self.ticker_b = available[1]
                print(f"Target pair not found in dataset. Using available pair: {self.ticker_a} / {self.ticker_b}")
        
        self.market_state = "FLAT"  # FLAT, LONG_SPREAD, SHORT_SPREAD

    def compute_signals(self, event) -> None:
        bars_df = self.data_handler.get_latest_bars(self.window + 10)
        if len(bars_df) < self.window:
            return

        prices_a = bars_df[self.ticker_a]
        prices_b = bars_df[self.ticker_b]

        # Compute spread (Price A - Price B ratio/difference or OLS hedge ratio approximation)
        # Using normalized price spread or price difference
        spread = prices_a - prices_b
        rolling_mean = spread.rolling(window=self.window).mean()
        rolling_std = spread.rolling(window=self.window).std()

        current_spread = spread.iloc[-1]
        mean_s = rolling_mean.iloc[-1]
        std_s = rolling_std.iloc[-1]

        if std_s == 0 or pd.isna(std_s):
            return

        z_score = (current_spread - mean_s) / std_s
        current_time = self.data_handler.get_latest_bar_datetime()

        # Z-Score Trading Logic:
        # 1. Short Spread (Z > entry_z): Spread is high -> Short Ticker A, Long Ticker B
        # 2. Long Spread (Z < -entry_z): Spread is low -> Long Ticker A, Short Ticker B
        # 3. Exit (|Z| < exit_z): Close positions
        
        if self.market_state == "FLAT":
            if z_score > self.entry_z:
                # Short spread: Sell A, Buy B
                self.events_queue.put(SignalEvent(current_time, self.ticker_a, 'SHORT', strength=abs(z_score)))
                self.events_queue.put(SignalEvent(current_time, self.ticker_b, 'LONG', strength=abs(z_score)))
                self.market_state = "SHORT_SPREAD"
            elif z_score < -self.entry_z:
                # Long spread: Buy A, Sell B
                self.events_queue.put(SignalEvent(current_time, self.ticker_a, 'LONG', strength=abs(z_score)))
                self.events_queue.put(SignalEvent(current_time, self.ticker_b, 'SHORT', strength=abs(z_score)))
                self.market_state = "LONG_SPREAD"
        
        elif self.market_state == "SHORT_SPREAD":
            if abs(z_score) <= self.exit_z:
                self.events_queue.put(SignalEvent(current_time, self.ticker_a, 'EXIT', strength=1.0))
                self.events_queue.put(SignalEvent(current_time, self.ticker_b, 'EXIT', strength=1.0))
                self.market_state = "FLAT"
                
        elif self.market_state == "LONG_SPREAD":
            if abs(z_score) <= self.exit_z:
                self.events_queue.put(SignalEvent(current_time, self.ticker_a, 'EXIT', strength=1.0))
                self.events_queue.put(SignalEvent(current_time, self.ticker_b, 'EXIT', strength=1.0))
                self.market_state = "FLAT"