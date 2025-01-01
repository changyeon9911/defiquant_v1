#lib settings
import warnings
import pandas as pd
from researcher import BinanceBacktestManager

# Sample Investment Table
def strat_bollinger_momentum(candlestick_df : pd.DataFrame, window=10):
    investment_df = candlestick_df.copy()[["Kline open time", "Kline Close time", "Open price", "Close price"]]
    investment_df["Previous Close price"] = investment_df["Close price"].shift(1)
    investment_df["std_window"] = investment_df["Previous Close price"].rolling(window).std()
    investment_df["boll_upper"] = investment_df["Previous Close price"].rolling(window).mean() + investment_df["std_window"]
    investment_df["boll_lower"] = investment_df["Previous Close price"].rolling(window).mean() - investment_df["std_window"]
    investment_df["Long Amount"] = (investment_df["Open price"] - investment_df["boll_upper"]).div(investment_df["std_window"])
    investment_df["Long Amount"] = investment_df["Long Amount"].fillna(0).clip(0)
    return investment_df

def volume_momentum(candlestick_df : pd.DataFrame, window=10):
    investment_df = candlestick_df.copy()[["Kline open time", "Kline Close time", "Open price", "Close price", "Quote asset volume"]]
    investment_df["Previous Volume"] = investment_df["Quote asset volume"].shift(1)
    investment_df["Long Amount"] = (investment_df["Previous Volume"] - investment_df["Previous Volume"].rolling(window).mean())/investment_df["Previous Volume"].rolling(10).mean()
    investment_df["Long Amount"] = investment_df["Long Amount"].fillna(0).clip(0)
    return investment_df

if __name__ == "__main__":
    
    warnings.filterwarnings(action='ignore')
    
    # ETH Candlestick Loader
    b_mangr_ETH = BinanceBacktestManager()
    b_mangr_ETH.load_params({"symbol" : "ETHUSDT", "interval" : "15m"})
    candlestick_df_ETH = b_mangr_ETH.get_candlestick()
    
    # SOL Candlestick Loader
    b_mangr_SOL = BinanceBacktestManager()
    b_mangr_SOL.load_params({"symbol" : "SOLUSDT", "interval" : "15m"})
    candlestick_df_SOL = b_mangr_SOL.get_candlestick()
    
    # PnL Dataframe
    pnl_df_train_ETH = b_mangr_ETH.backtest(starting_usdt=50, investment_df=volume_momentum(candlestick_df_ETH, window=20));
    pnl_df_train_SOL = b_mangr_SOL.backtest(starting_usdt=50, investment_df=volume_momentum(candlestick_df_SOL, window=20));
    
    pnl_df_train = pnl_df_train_ETH.copy()
    pnl_df_train["cumulative_pnl"] += pnl_df_train_SOL["cumulative_pnl"]
    
    #visualization
    b_mangr_ETH.visualize_pnl(pnl_df_train, test=True)