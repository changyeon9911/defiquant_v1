#lib settings
import warnings
import pandas as pd
from researcher import BinanceBacktestManager

# Sample Investment Table
def strat_bollinger_momentum(candlestick_df : pd.DataFrame):
    investment_df = candlestick_df.copy()[["Kline open time", "Kline Close time", "Open price", "Close price"]]
    investment_df["Previous Close price"] = investment_df["Close price"].shift(1)
    investment_df["std_window_10"] = investment_df["Previous Close price"].rolling(10).std()
    investment_df["boll_upper"] = investment_df["Previous Close price"].rolling(10).mean() + 1.96 * investment_df["std_window_10"]
    investment_df["boll_lower"] = investment_df["Previous Close price"].rolling(10).mean() - 1.96 * investment_df["std_window_10"]
    investment_df["Long Amount"] = (investment_df["Open price"] - investment_df["boll_upper"]).div(investment_df["std_window_10"]).fillna(0).clip(0)
    return investment_df

if __name__ == "__main__":
    
    warnings.filterwarnings(action='ignore')
    
    # Candlestick Loader
    b_mangr = BinanceBacktestManager()
    b_mangr.load_params({"symbol" : "ETHUSDT", "interval" : "15m"})
    candlestick_df = b_mangr.get_candlestick()

    # PnL Dataframe
    pnl_df_train = b_mangr.backtest(starting_usdt=100, investment_df=strat_bollinger_momentum(candlestick_df));

    #visualization
    b_mangr.visualize_pnl(pnl_df_train, test=True)