import queue
import time
import pandas as pd

# Robust import handling for direct script execution vs package module execution
try:
    from src.data_handler import ParquetDataHandler
    from src.portfolio import Portfolio
    from src.execution import SimulatedExecutionHandler
except ImportError:
    from data_handler import ParquetDataHandler
    from portfolio import Portfolio
    from execution import SimulatedExecutionHandler


class Backtester:
    """
    Orchestrates the event-driven backtesting loop by consuming 
    and dispatching events between the DataHandler, Strategy, Portfolio, and ExecutionHandler.
    """
    def __init__(self, parquet_path: str = "data/cleaned_prices.parquet", initial_capital: float = 100000.0):
        self.events_queue = queue.Queue()
        self.data_handler = ParquetDataHandler(self.events_queue, parquet_path)
        self.portfolio = Portfolio(self.data_handler, self.events_queue, initial_capital)
        self.execution_handler = SimulatedExecutionHandler(self.data_handler, self.events_queue)
        self.strategy = None

    def set_strategy(self, strategy_instance) -> None:
        """Injects a trading strategy into the backtester loop."""
        self.strategy = strategy_instance

    def run_backtest(self) -> pd.DataFrame:
        """
        Executes the main event-driven loop until all historical bars are consumed.
        """
        print("Starting event-driven backtest loop...")
        start_time = time.time()
        iterations = 0

        while self.data_handler.continue_backtest:
            # 1. Advance market data stream (pushes MarketEvent to queue)
            has_data = self.data_handler.update_market_data()
            if not has_data:
                break

            # 2. Process all events currently in the queue until empty
            while True:
                try:
                    event = self.events_queue.get(block=False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.portfolio.update_timeindex(event)
                            if self.strategy:
                                self.strategy.compute_signals(event)
                        elif event.type == 'SIGNAL':
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':
                            self.portfolio.update_fill(event)
            
            iterations += 1

        duration = time.time() - start_time
        print(f"Backtest completed in {duration:.2f} seconds across {iterations} bars.")
        print(f"Final Portfolio Equity: ${self.portfolio.total_equity:,.2f}")
        
        return pd.DataFrame(self.portfolio.all_holdings)

if __name__ == "__main__":
    bt = Backtester()
    equity_curve = bt.run_backtest()
    print("\nLast 5 equity snapshots:")
    print(equity_curve.tail())