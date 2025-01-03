import os
from dotenv import load_dotenv
from .TradeFilter import TradeFilter
from external_api.exchange.binance.BinanceInterface import BinanceInterface

class BinanceTradeFilter(TradeFilter):

    def __init__(self):
        super().__init__()
        
        #AUTH
        load_dotenv()
        BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
        BINANCE_SECRET_KEY_PATH = os.environ.get("BINANCE_PRIVATE_KEY_PATH")
        self.interface = BinanceInterface(BINANCE_API_KEY, BINANCE_SECRET_KEY_PATH)

        #instance var
        self.filters = None
    
    def load_filters(self, symbol : str):
        exchange_info = self.interface.exchange_info({"symbol" : symbol})
        self.filters = exchange_info.json().get("symbols")[0]["filters"]

    def apply_filters(self, qty : float):
        #do for LOT_SIZE
        try:
            lot_size_filter = [ft for ft in self.filters if ft["filterType"] == 'LOT_SIZE'][0]
            truncated_qty = min(max(qty, float(lot_size_filter["minQty"])), float(lot_size_filter["maxQty"]))
            rounded_qty = int(truncated_qty // float(lot_size_filter["stepSize"])) * float(lot_size_filter["stepSize"])
            return rounded_qty
        except:
            return None
        #do for NOTIONAL
        #try:
        #    notional_filter = [ft for ft in self.filters if ft["filterType"] == 'NOTIONAL'][0]
        #    print(notional_filter)
        #    return rounded_qty
        #except:
        #    return None

if __name__ == "__main__":
    filter = BinanceTradeFilter()
    filter.load_filters("SOLUSDT")
    filter.apply_filters(0.00015134791204)