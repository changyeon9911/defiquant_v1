from .Distributor import Distributor
from ..order import UpbitOrderManager
from ..strategy import UpbitStrategyManager

class UpbitDistributor(Distributor):

    def __init__(self, symbols : list):
        self.symbols = symbols
        self.order_managers = [UpbitOrderManager()] * len(symbols)
        self.strat_managers = [UpbitStrategyManager()] * len(symbols)
    
    def get_strat_managers(self):
        return self.strat_managers
    
    def get_order_managers(self):
        return self.order_managers