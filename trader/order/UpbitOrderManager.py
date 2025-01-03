import os
import pandas as pd
from dotenv import load_dotenv
from .OrderManager import OrderManager
from external_api.exchange.upbit.UpbitInterface import UpbitInterface

class UpbitOrderManager(OrderManager):
    """
    UpbitOrderManager Class Has Responsibility for:
        - Retrieve Buy/Sell Orders From StrategyManager
        - Execute Buy/Sell Orders on upbit
    """

    def __init__(self):
        super().__init__()

        #AUTH
        load_dotenv()
        UPBIT_API_ACCESS_KEY = os.environ.get("UPBIT_API_ACCESS_KEY")
        UPBIT_API_SECRET_KEY = os.environ.get("UPBIT_API_SECRET_KEY")
        self.interface = UpbitInterface(UPBIT_API_ACCESS_KEY, UPBIT_API_SECRET_KEY)

    def retrieve_orders(self, orders : dict):
        self.orders = orders
        return

    def excute_orders(self):
        response = self.interface.make_new_order(self.orders)
        return response

