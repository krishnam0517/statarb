import pandas as pd
from src.backtester import Backtester
from src.strategy import PairsTradingStrategy

def run_pairs():
    print("Initializing Stat-Arb Pairs Trading Backtest...")
    bt = Backtester(initial_capital=100000.0)
    
    # Instantiate Pairs Strategy (e.g., KO and PEP, or first two available tickers)
    strategy = PairsTradingStrategy(
        bt.data_handler, 
        bt.events_queue, 
        ticker_a='KO', 
        ticker_b='PEP', 
        window=60, 
        entry_z=2.0, 
        exit_z=0.5
    )
    bt.set_strategy(strategy)
    
    equity_df = bt.run_backtest()
    
    print("\n==========================================")
    print("      PAIRS TRADING BACKTEST RESULTS      ")
    print("==========================================")
    print(f"Initial Capital: $100,000.00")
    print(f"Final Equity:    ${equity_df['equity'].iloc[-1]:,.2f}")
    total_return = ((equity_df['equity'].iloc[-1] - 100000.0) / 100000.0) * 100
    print(f"Total Return:    {total_return:.2f}%")
    print("==========================================")

if __name__ == "__main__":
    run_pairs()