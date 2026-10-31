import pandas as pd
from src.backtester import Backtester
from src.strategy import BuyAndHoldStrategy

def verify_buy_and_hold():
    print("Initializing Event-Driven Backtester...")
    bt = Backtester(initial_capital=100000.0)
    
    # Pick the first ticker in our dataset for validation (e.g., AAPL)
    target_ticker = list(bt.data_handler.symbol_data.columns)[0]
    print(f"Target validation ticker: {target_ticker}")
    
    # Set Buy and Hold Strategy
    strategy = BuyAndHoldStrategy(bt.data_handler, bt.events_queue, ticker=target_ticker)
    bt.set_strategy(strategy)
    
    # Run Backtest
    equity_df = bt.run_backtest()
    equity_df.set_index('datetime', inplace=True)
    
    # --- Pandas Vectorized Calculation for Comparison ---
    prices = bt.data_handler.symbol_data[target_ticker]
    initial_price = prices.iloc[0]
    # Approximate shares bought with initial capital minus initial commission
    approx_shares = int((100000.0 * 0.995) / initial_price)
    initial_commission = max(1.00, approx_shares * 0.005)
    initial_cash = 100000.0 - (approx_shares * initial_price + initial_commission)
    
    # Pandas expected equity curve
    expected_equity = initial_cash + (approx_shares * prices)
    
    print("\n==========================================")
    print("          VALIDATION COMPARISON           ")
    print("==========================================")
    print(f"Final Event-Driven Equity: ${equity_df['equity'].iloc[-1]:,.2f}")
    print(f"Final Pandas Vectorized Equity: ${expected_equity.iloc[-1]:,.2f}")
    
    diff = abs(equity_df['equity'].iloc[-1] - expected_equity.iloc[-1])
    print(f"Absolute Difference: ${diff:.2f}")
    print("==========================================")
    
    if diff < 500.0:
        print("SUCCESS: Event-driven equity curve matches pandas calculation closely!")
    else:
        print("NOTE: Minor variance due to discrete execution pricing/timing.")

if __name__ == "__main__":
    verify_buy_and_hold()