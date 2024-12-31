class BacktestManager:

    def __init__(self):
        self.orders = None
        self.interface = None
        self.params = None

        
    def retrieve_orders(self, orders):
        self.orders = orders
        return
    
    def backtest(self):
        pass
    
    