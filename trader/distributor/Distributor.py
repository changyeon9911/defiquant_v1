from ..strategy import StrategyManager
from ..order import OrderManager

class Distributor:
    def __init__(self, symbols : list):
        self.symbols = symbols
        self.order_managers = [OrderManager()] * len(symbols)
        self.strat_managers = [StrategyManager()] * len(symbols)
    
    def get_strat_managers(self):
        return self.strat_managers
    
    def get_order_managers(self):
        return self.order_managers