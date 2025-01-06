import time
import warnings
from pytz import timezone # type: ignore
from datetime import datetime
from trader import UpbitStrategyManager, UpbitOrderManager

BASE = "DOGE"
QUOTE = "KRW"
SYMBOL = f"{QUOTE}-{BASE}"
INTERVAL = 24
UNIT = "days"
IS_MINUTES = 1 if (UNIT == "minutes") else 0
ORDER_TYPE = "MARKET"

if __name__ == "__main__":
    
    warnings.filterwarnings(action='ignore')

    Upbit_om = UpbitOrderManager()
    Upbit_sm = UpbitStrategyManager()

    long_amt = 0
    sell_amt = 0
    notyet_traded = True

    while True:
        now = datetime.now().astimezone(timezone("Asia/Seoul"))
        hour = now.hour
        if (hour % INTERVAL == 0):
            if notyet_traded:
                long_amt = Upbit_sm.volume_momentum({"market" : f"{QUOTE}-{BASE}"}, window=10, interval=(IS_MINUTES * INTERVAL), unit="days")
                if (long_amt > 0):
                    order_dict = {"market" : f"{QUOTE}-{BASE}", "side" : "bid", "ord_type" : "price", "price" : long_amt}
                    Upbit_om.retrieve_orders(order_dict)
                    order_response = Upbit_om.excute_orders()
                    if (order_response.status_code == 201):
                        #price = order_response["fills"][0]["price"]
                        #qty = order_response["fills"][0]["qty"]
                        #commission = order_response["fills"][0]["commission"]
                        #long_amt = round(Upbit_ft.apply_filters(float(eval(f'{qty} - ({commission} / {price})'))) - 0.00005, 4)
                        print("PROCESSED(BUY) : ", datetime.now().astimezone(timezone("Asia/Seoul")))
                    else:
                        long_amt = 0
                        sell_amt = 0
                        print("FAILED TO BUY", datetime.now().astimezone(timezone("Asia/Seoul")))
                        print("\tDETAILS : ", order_response.content)
                else:
                    print("SKIPPED", datetime.now().astimezone(timezone("Asia/Seoul")))
                notyet_traded = False
        elif ((hour % INTERVAL == INTERVAL-1)):
            if not notyet_traded:
                try:
                    userdata = Upbit_sm.backtest_manager.get_userdata().json()
                    sell_amt = float([info["balance"] for info in userdata if (info["currency"] == f"{BASE}")][0])
                except:
                    sell_amt = 0
                if (sell_amt > 0):
                    timestamp = int(time.time() * 1000.0)
                    order_dict = {"market" : f"{QUOTE}-{BASE}", "side" : "ask", "ord_type" : "market", "volume" : sell_amt}
                    Upbit_om.retrieve_orders(order_dict)
                    order_response = Upbit_om.excute_orders()
                    if (order_response.status_code == 201):
                        print("PROCESSED(SELL) : ", datetime.now().astimezone(timezone("Asia/Seoul")))
                    else:
                        print("FAILED TO SELL", datetime.now().astimezone(timezone("Asia/Seoul")))
                        print("\tDETAILS : ", order_response.content)
                long_amt = 0
                sell_amt = 0
                notyet_traded = True
            
