import time
import warnings
from pytz import timezone # type: ignore
from datetime import datetime
from trader import BinanceStrategyManager, BinanceOrderManager, BinanceTradeFilter

BASE = "DOGE"
QUOTE = "USDT"
SYMBOL = f"{BASE}{QUOTE}"
INTERVAL = "1d"
INTERVAL_INT = 24
BUY = "BUY"
SELL = "SELL"
ORDER_TYPE = "MARKET"

if __name__ == "__main__":
    
    warnings.filterwarnings(action='ignore')

    binance_om = BinanceOrderManager()
    binance_sm = BinanceStrategyManager()
    binance_ft = BinanceTradeFilter()

    long_amt = 0
    sell_amt = 0
    notyet_traded = True
    binance_ft.load_filters(SYMBOL)

    while True:
        now = datetime.now()
        hour = now.hour
        if (hour % INTERVAL_INT == 0):
            if notyet_traded:
                long_amt = round(binance_ft.apply_filters(binance_sm.volume_momentum({"symbol" : SYMBOL, "interval" : INTERVAL}, window=40))-0.00005, 4)
                if (long_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : BUY, "type" : ORDER_TYPE, "quantity" : long_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    order_response = binance_om.excute_orders()
                    if (order_response.status_code == 200):
                        #price = order_response["fills"][0]["price"]
                        #qty = order_response["fills"][0]["qty"]
                        #commission = order_response["fills"][0]["commission"]
                        #long_amt = round(binance_ft.apply_filters(float(eval(f'{qty} - ({commission} / {price})'))) - 0.00005, 4)
                        sell_amt = round(float([balance for balance in binance_sm.backtest_manager.get_userdata().json().get("balances") if (balance["asset"] == BASE)][0]["free"]) - 0.00005, 4)
                        print("PROCESSED(BUY) : ", datetime.now().astimezone(timezone("Asia/Seoul")))
                    else:
                        long_amt = 0
                        sell_amt = 0
                        print("FAILED TO BUY", datetime.now().astimezone(timezone("Asia/Seoul")))
                        print("\tDETAILS : ", order_response.content)
                else:
                    print("SKIPPED", datetime.now().astimezone(timezone("Asia/Seoul")))
                notyet_traded = False
        elif ((hour % INTERVAL_INT == INTERVAL_INT-1)):
            if not notyet_traded:
                if (sell_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"symbol" : SYMBOL, "side" : SELL, "type" : ORDER_TYPE, "quantity" : sell_amt, "timestamp" : timestamp}
                    binance_om.retrieve_orders(order_dict)
                    order_response = binance_om.excute_orders()
                    if (order_response.status_code == 200):
                        print("PROCESSED(SELL) : ", datetime.now().astimezone(timezone("Asia/Seoul")))
                    else:
                        print("FAILED TO SEL", datetime.now().astimezone(timezone("Asia/Seoul")))
                        print("\tDETAILS : ", order_response.content)
                long_amt = 0
                sell_amt = 0
                notyet_traded = True
            
