import time
import warnings
from pytz import timezone # type: ignore
from datetime import datetime
from multiprocessing import Pool
from trader import UpbitStrategyManager, UpbitOrderManager, UpbitDistributor

BASES = ["DOGE", "ETH", "BTC"]
QUOTE = "KRW"
SYMBOLS = [f"{QUOTE}-{base}" for base in BASES]
INTERVAL = 24
UNIT = "days"
IS_MINUTES = 1 if (UNIT == "minutes") else 0
ORDER_TYPE = "MARKET"
WINDOW = 10

def functionalized_volume_momentum(core : tuple, window=WINDOW, interval=INTERVAL*IS_MINUTES, unit=UNIT):
    upbit_strategy_manager, params_dict = core
    long_amt = upbit_strategy_manager.volume_momentum(params_dict=params_dict, window=window, interval=interval, unit=unit)
    return long_amt

if __name__ == "__main__":
    
    warnings.filterwarnings(action='ignore')

    long_amt_list = []
    sell_amt_list = []
    notyet_traded = True
    
    upbit_dist = UpbitDistributor(SYMBOLS)
    
    while True:
        now = datetime.now().astimezone(timezone("Asia/Seoul"))
        hour = now.hour
        if (hour % INTERVAL != 0):
            if notyet_traded:
                arguments = [(mngr, {"market" : f"{QUOTE}-{base}"}) for mngr, base in zip(upbit_dist.get_strat_managers(), BASES)]
                with Pool(len(SYMBOLS)) as p:
                    long_amt_list = p.map(functionalized_volume_momentum, arguments)
                print(long_amt_list)
                notyet_traded = False
                