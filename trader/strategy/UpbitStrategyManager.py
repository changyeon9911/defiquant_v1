#lib_settings
import json
import pandas as pd # type: ignore
from researcher import UpbitBacktestManager
from .StrategyManager import StrategyManager

class UpbitStrategyManager(StrategyManager):
    
    def __init__(self):
        #AUTH
        self.backtest_manager = UpbitBacktestManager()

    def upto_balance(self, desired_ratio, commission_rate=0.001):
        
        userdata = self.backtest_manager.get_userdata().json()
        free_krw = float([info["balance"] for info in userdata if (info["currency"] == "KRW")][0])
        free_krw_if_commission = free_krw/(1+commission_rate)
        return max(min(free_krw_if_commission, free_krw_if_commission * desired_ratio), 0.1 * free_krw_if_commission) * (1+commission_rate)

#    Yet on work        
#    def apply_filters(self, params_dict : dict):
#        return self.backtest_manager.interface.exchange_info(params_dict)

    def volume_momentum(self, params_dict : dict, window=10):

        def volume_momentum(candlestick_df : pd.DataFrame, window=10):
            investment_df = candlestick_df.copy()[["candle_date_time_utc", "opening_price", "trade_price", "candle_acc_trade_price"]]
            investment_df["Previous Volume"] = investment_df["candle_acc_trade_price"].shift(1)
            investment_df["Long Ratio"] = (investment_df["candle_acc_trade_price"] - investment_df["Previous Volume"].rolling(window).mean())/investment_df["Previous Volume"].rolling(window).mean()
            investment_df["Long Ratio"] = investment_df["Long Ratio"].fillna(0).clip(lower=0, upper=1)
            return investment_df

        self.backtest_manager.load_params(params_dict)
        candlestick_df = self.backtest_manager.get_candlestick()    

        final_long_amount = self.upto_balance(volume_momentum(candlestick_df, window=window).iloc[-1]["Long Ratio"])
        return final_long_amount