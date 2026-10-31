import queue

# Robust import handling for direct script execution vs package module execution
try:
    from src.events import OrderEvent, FillEvent
except ImportError:
    from events import OrderEvent, FillEvent


class SimulatedExecutionHandler:
    """
    The SimulatedExecutionHandler converts OrderEvents into FillEvents 
    by assuming instant execution at the latest available market price.
    """
    def __init__(self, data_handler, events_queue: queue.Queue):
        self.data_handler = data_handler
        self.events_queue = events_queue

    def execute_order(self, event: OrderEvent) -> None:
        """
        Converts an OrderEvent into a FillEvent using the latest bar price.
        """
        if event.type == 'ORDER':
            current_time = self.data_handler.get_latest_bar_datetime()
            ticker = event.ticker
            
            try:
                # Get execution price (latest available bar price)
                execution_price = self.data_handler.get_latest_bar(ticker)
                
                # Generate FillEvent
                fill_event = FillEvent(
                    timestamp=current_time,
                    ticker=ticker,
                    quantity=event.quantity,
                    direction=event.direction,
                    fill_cost=execution_price
                )
                
                # Push fill to queue for the Portfolio to consume
                self.events_queue.put(fill_event)
            except Exception as e:
                print(f"Execution error for order {event}: {e}")