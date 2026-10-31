import queue
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from src.events import OrderEvent, FillEvent
except ImportError:
    from events import OrderEvent, FillEvent


class Portfolio:
    def __init__(self, data_handler, events_queue: queue.Queue, initial_capital: float = 100000.0):
        self.data_handler = data_handler
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        
        self.bars = 0
        self.datetime = self.data_handler.get_latest_bar_datetime()
        
        self.current_positions = {ticker: 0 for ticker in self.data_handler.symbol_data.columns}
        self.current_holdings = {ticker: 0.0 for ticker in self.data_handler.symbol_data.columns}
        
        self.cash = initial_capital
        self.total_equity = initial_capital
        
        self.all_holdings = []

    def update_timeindex(self, event) -> None:
        self.bars += 1
        self.datetime = self.data_handler.get_latest_bar_datetime()
        
        market_value_holdings = 0.0
        for ticker in self.current_positions.keys():
            try:
                price = self.data_handler.get_latest_bar(ticker)
                val = self.current_positions[ticker] * price
                self.current_holdings[ticker] = val
                market_value_holdings += val
            except KeyError:
                pass
        
        self.total_equity = self.cash + market_value_holdings
        
        self.all_holdings.append({
            'datetime': self.datetime,
            'cash': self.cash,
            'market_value': market_value_holdings,
            'equity': self.total_equity
        })

    def update_signal(self, event) -> None:
        if event.type == 'SIGNAL':
            ticker = event.ticker
            direction = event.signal_type
            
            try:
                price = self.data_handler.get_latest_bar(ticker)
                allocation_capital = self.cash * 0.995
                quantity = int(allocation_capital / price)
                
                if quantity > 0 and direction == 'LONG' and self.current_positions[ticker] == 0:
                    order = OrderEvent(self.datetime, ticker, 'MKT', quantity, 'BUY')
                    self.events_queue.put(order)
            except Exception as e:
                print(f"Error generating order for {ticker}: {e}")

    def update_fill(self, event: FillEvent) -> None:
        fill_dir = 1 if event.direction == 'BUY' else -1
        cost = event.fill_cost
        quantity = event.quantity
        commission = event.commission
        
        cash_change = fill_dir * quantity * cost + commission
        self.cash -= cash_change
        self.current_positions[event.ticker] += fill_dir * quantity