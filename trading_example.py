import time
import warnings
from pytz import timezone
from datetime import datetime
from trader import BinanceStrategyManager, BinanceOrderManager

BASE = "ETH"
QUOTE = "USDT"
SYMBOL = f"{BASE}{QUOTE}"
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
        if (minute % 15 == 0):
            if notyet_traded:
                long_amt = binance_sm.volume_momentum({"symbol" : SYMBOL, "interval" : INTERVAL}, window=20)
                if (long_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : BUY, "type" : ORDER_TYPE, "quantity" : long_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    order_response = eval(binance_om.excute_orders())
                    try:
                        price = order_response["fills"][0]["price"]
                        qty = order_response["fills"][0]["qty"]
                        commission = order_response["fills"][0]["commission"]
                        long_amt = round(eval(f'{qty} - ({commission} / {price})') - 0.00005, 4)
                        print("PROCESSED", datetime.now().astimezone(timezone("Asia/Seoul")))
                    except:
                        long_amt = 0
                        print("FAILED TO BUY", datetime.now().astimezone(timezone("Asia/Seoul")))
                        print("DETAILS : ", order_response)
                else:
                    print("SKIPPED", datetime.now().astimezone(timezone("Asia/Seoul")))
                notyet_traded = False
        elif (minute % 15 == 14):
            if not notyet_traded:
                if (long_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : SELL, "type" : ORDER_TYPE, "quantity" : long_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    order_response = binance_om.excute_orders()
                    print("SELL : ", order_response)
                notyet_traded = True
            
