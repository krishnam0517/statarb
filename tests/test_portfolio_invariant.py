import os
import pandas as pd
import queue

try:
    from src.backtester import Backtester
    from src.strategy import BuyAndHoldStrategy
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.backtester import Backtester
    from src.strategy import BuyAndHoldStrategy


def test_equity_invariant():
    """
    Verifies that Equity == Cash + Market Value of Positions at every step of the backtest.
    """
    print("Initializing Backtester for Portfolio Invariant Test...")
    bt = Backtester(initial_capital=100000.0)
    
    target_ticker = list(bt.data_handler.symbol_data.columns)[0]
    strategy = BuyAndHoldStrategy(bt.data_handler, bt.events_queue, ticker=target_ticker)
    bt.set_strategy(strategy)
    
    equity_df = bt.run_backtest()
    
    # Check invariant across all recorded snapshots
    equity_df['calculated_equity'] = equity_df['cash'] + equity_df['market_value']
    equity_df['difference'] = (equity_df['equity'] - equity_df['calculated_equity']).abs()
    
    max_diff = equity_df['difference'].max()
    print(f"\nMax Invariant Discrepancy (Equity vs Cash + Positions): ${max_diff:.10f}")
    
    assert max_diff < 1e-6, f"Portfolio invariant violated! Max discrepancy: {max_diff}"
    print("SUCCESS: Portfolio invariant (Equity = Cash + Positions) holds true across all steps!")


if __name__ == "__main__":
    test_equity_invariant()