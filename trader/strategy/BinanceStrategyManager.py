#lib_settings
import pandas as pd
from researcher import BinanceBacktestManager
from .StrategyManager import StrategyManager

class BinanceStrategyManager(StrategyManager):
    
    def __init__(self):
        #AUTH
        self.backtest_manager = BinanceBacktestManager()

    def upto_balance(self, desired_amount, base, commission_rate=0.001):
        
        free_usdt = float([balance for balance in self.backtest_manager.get_userdata().json().get("balances") if (balance["asset"] == "USDT")][0]["free"])
        free_usdt_if_commission = round(free_usdt/(1+commission_rate) - 0.00005, 4)
        free_base_if_commission = free_usdt_if_commission/float(self.backtest_manager.interface.get_current_price({"symbol" : base}).json().get("price"))
        return round(min(free_base_if_commission, desired_amount) * (1+commission_rate) - 0.00005, 4)

#    Yet on work        
#    def apply_filters(self, params_dict : dict):
#        return self.backtest_manager.interface.exchange_info(params_dict)

    def bollinger_momentum(self, params_dict : dict):

        def strat_bollinger_momentum(candlestick_df : pd.DataFrame, window=10):
            investment_df = candlestick_df.copy()[["Kline open time", "Kline Close time", "Open price", "Close price"]]
            investment_df["Previous Close price"] = investment_df["Close price"].shift(1)
            investment_df["std_window"] = investment_df["Previous Close price"].rolling(window).std()
            investment_df["boll_upper"] = investment_df["Previous Close price"].rolling(window).mean() + 1.96 * investment_df["std_window"]
            investment_df["boll_lower"] = investment_df["Previous Close price"].rolling(window).mean() - 1.96 * investment_df["std_window"]
            investment_df["Long Amount"] = (investment_df["Open price"] - investment_df["boll_upper"]).div(investment_df["std_window"]).fillna(0).clip(0)
            return investment_df

        self.backtest_manager.load_params(params_dict)
        candlestick_df = self.backtest_manager.get_candlestick()    

        final_long_amount = self.upto_balance(strat_bollinger_momentum(candlestick_df).iloc[-1]["Long Amount"], base=params_dict["symbol"])
        return final_long_amount

    def volume_momentum(self, params_dict : dict, window=10):

        def volume_momentum(candlestick_df : pd.DataFrame, window=window):
            investment_df = candlestick_df.copy()[["Kline open time", "Kline Close time", "Open price", "Close price", "Quote asset volume"]]
            investment_df["Previous Volume"] = investment_df["Quote asset volume"].shift(1)
            investment_df["Long Amount"] = (investment_df["Previous Volume"] - investment_df["Previous Volume"].rolling(window).mean())/investment_df["Previous Volume"].rolling(10).mean()
            investment_df["Long Amount"] = investment_df["Long Amount"].fillna(0).clip(0)
            return investment_df

        self.backtest_manager.load_params(params_dict)
        candlestick_df = self.backtest_manager.get_candlestick()    

        final_long_amount = self.upto_balance(volume_momentum(candlestick_df, window=window).iloc[-1]["Long Amount"], base=params_dict["symbol"])
        return final_long_amount