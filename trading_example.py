import time
import warnings
from datetime import datetime
from trader import BinanceStrategyManager, BinanceOrderManager

SYMBOL = "ETHUSDT"
INTERVAL = "15m"
BUY = "BUY"
SELL = "SELL"
ORDER_TYPE = "MARKET"

if __name__ == "__main__":

    warnings.filterwarnings(action='ignore')

    binance_om = BinanceOrderManager()
    binance_sm = BinanceStrategyManager()

    long_amt = 0
    notyet_traded = True

    while True:
        now = datetime.now()
        minute = now.minute
        second = now.second
        if ((minute % 15 == 0) & (second > 30)):
            if notyet_traded:
                long_amt = binance_sm.volume_momentum({"symbol" : SYMBOL, "interval" : INTERVAL}, window=20) * 0.99
                if (long_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : BUY, "type" : ORDER_TYPE, "quantity" : long_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    binance_om.excute_orders()
                    print("PROCESSED", datetime.now())
                else:
                    print("SKIPPED", datetime.now())
                notyet_traded = False

        elif ((minute % 15 == 14) & (second > 30)):
            if not notyet_traded:
                if (long_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : SELL, "type" : ORDER_TYPE, "quantity" : long_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    binance_om.excute_orders()
                notyet_traded = True


            
