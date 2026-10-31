from abc import ABC, abstractmethod
import queue

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
    """
    Buys a target ticker on the first bar and holds for the backtest duration.
    """
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