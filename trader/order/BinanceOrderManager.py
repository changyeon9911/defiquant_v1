import os
import pandas as pd
from dotenv import load_dotenv
from .OrderManager import OrderManager
from external_api.exchange.binance.BinanceInterface import BinanceInterface

class BinanceOrderManager(OrderManager):
    """
    BinanaceOrderManager Class Has Responsibility for:
        - Retrieve Buy/Sell Orders From StrategyManager
        - Execute Buy/Sell Orders on Binance
    """

    def __init__(self):
        super().__init__()

        #AUTH
        load_dotenv()
        BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
        BINANCE_SECRET_KEY_PATH = os.environ.get("BINANCE_PRIVATE_KEY_PATH")
        self.interface = BinanceInterface(BINANCE_API_KEY, BINANCE_SECRET_KEY_PATH)

    def retrieve_orders(self, orders : dict):
        self.orders = orders
        return

    def excute_orders(self):
        if (self.interface.test_connectivity()):
            response = self.interface.make_new_order(self.orders)
            return response

