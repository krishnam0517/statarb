class CostModel:
    """
    Calculates commissions, half-spreads, market impact, and borrow fees 
    for equity and stat-arb order executions.
    """
    def __init__(
        self,
        commission_per_share: float = 0.005,
        min_commission: float = 1.00,
        half_spread_bps: float = 2.0,      # 2 basis points default half-spread
        impact_coefficient: float = 0.1,    # Square-root market impact parameter
        annual_borrow_rate: float = 0.005   # 50 bps annual fee for short borrows
    ):
        self.commission_per_share = commission_per_share
        self.min_commission = min_commission
        self.half_spread_bps = half_spread_bps
        self.impact_coefficient = impact_coefficient
        self.annual_borrow_rate = annual_borrow_rate

    def calculate_commission(self, quantity: int) -> float:
        """Calculates tiered commission fee with a minimum threshold."""
        return max(self.min_commission, abs(quantity) * self.commission_per_share)

    def calculate_execution_cost(self, price: float, quantity: int, direction: str, volume: float = None) -> float:
        """
        Calculates effective execution cost per share including half-spread 
        and temporary market impact.
        """
        # Half-spread cost (slippage towards the aggressive side)
        spread_cost = price * (self.half_spread_bps / 10000.0)
        
        # Temporary market impact (simplified square-root participation model if volume is known)
        impact_cost = 0.0
        if volume and volume > 0:
            participation_rate = abs(quantity) / volume
            impact_cost = price * self.impact_coefficient * (participation_rate ** 0.5)
        
        effective_price = price + spread_cost + impact_cost if direction.upper() == 'BUY' else price - spread_cost - impact_cost
        return effective_price

    def calculate_borrow_fee(self, position_value: float, days_held: int = 1) -> float:
        """
        Calculates the overnight stock borrowing fee for short positions.
        """
        if position_value <= 0:
            return 0.0
        daily_rate = self.annual_borrow_rate / 365.0
        return position_value * daily_rate * days_held

if __name__ == "__main__":
    model = CostModel()
    qty = 1000
    px = 150.0
    comm = model.calculate_commission(qty)
    exec_px = model.calculate_execution_cost(px, qty, 'BUY')
    print(f"Quantity: {qty} | Base Price: ${px:.2f} | Execution Price: ${exec_px:.2f} | Commission: ${comm:.2f}")