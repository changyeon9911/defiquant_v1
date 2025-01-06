from .Distributor import Distributor
from ..order import BinanceOrderManager
from ..strategy import BinanceStrategyManager

class BinanceDistributor(Distributor):

    def __init__(self, symbols : list):
        self.symbols = symbols
        self.order_managers = [BinanceOrderManager()] * len(symbols)
        self.strat_managers = [BinanceStrategyManager()] * len(symbols)
    
    def get_strat_managers(self):
        return self.strat_managers
    
    def get_order_managers(self):
        return self.order_managers