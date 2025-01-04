import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from .BacktestManager import BacktestManager
from external_api.exchange.binance import BinanceInterface

class BinanceBacktestManager(BacktestManager):
    """
    BinanceBacktesetManager Class Has Responsibility for:
        - Retrieve Binance Statistics 
        - Retrieve Buy/Sell Orders
        - Execute Buy/Sell Orders Backtest with Binance Data
    """
    CANDLESTICK_SYMBOL = "ETHUSDT"
    CANDLESTICK_INTERVAL = "1m"
    CANDLESTICK_LIMIT = 1000
    CANDLESTICK_COLS = ["Kline open time", "Open price", "High price", "Low price", "Close price", "Volume", "Kline Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Unused field"]

    def __init__(self):
        super().__init__()
        
        #AUTH
        load_dotenv()
        BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
        BINANCE_SECRET_KEY_PATH = os.environ.get("BINANCE_PRIVATE_KEY_PATH")
        self.interface = BinanceInterface(BINANCE_API_KEY, BINANCE_SECRET_KEY_PATH)
        
    def load_params(self, params : dict = None):
        if params is None:
            self.params = {"symbol" : self.CANDLESTICK_SYMBOL, "interval" : self.CANDLESTICK_INTERVAL, "limit" : self.CANDLESTICK_LIMIT}
        else:
            self.params = {"symbol" : self.CANDLESTICK_SYMBOL, "interval" : self.CANDLESTICK_INTERVAL, "limit" : self.CANDLESTICK_LIMIT}
            for key in params.keys():
                self.params[key] = params[key]

    def get_statistics_24hr(self):
        statistics = self.interface.get_statistics(self.params);
        return statistics
    
    def get_userdata(self):
        userdata = self.interface.get_userdata();
        return userdata

    def get_candlestick(self, test_ratio = 0.2):
        #datetime columns
        candlestick_df = pd.DataFrame(self.interface.get_candlestick(self.params).json(), columns=self.CANDLESTICK_COLS)
        candlestick_df["Kline open time"] = pd.to_datetime(candlestick_df["Kline open time"], unit='us', utc=True).dt.tz_convert("Asia/Seoul")
        candlestick_df["Kline Close time"] = pd.to_datetime(candlestick_df["Kline Close time"], unit='us', utc=True).dt.tz_convert("Asia/Seoul")

        #numeric columns
        numeric_columns = [col for col in list(set(candlestick_df.columns) - set({"Kline open time", "Kline Close time"}))]
        candlestick_df[numeric_columns] = candlestick_df[numeric_columns].astype("float64")

        return candlestick_df
    
    def backtest(self, starting_usdt, investment_df : pd.DataFrame, commission_rate=0.001):
        investment_df["commission"] = 0
        investment_df["marginal_pnl"] = 0
        investment_df["max_long_amt"] = 0
        investment_df["cumulative_pnl"] = 0
        investment_df.loc[0, "cumulative_pnl"] = starting_usdt

        for i in range(len(investment_df)-1):
            investment_df.loc[i+1, "max_long_amt"] = investment_df.loc[i, "cumulative_pnl"]/investment_df.loc[i+1, "Open price"]
            investment_df.loc[i+1, "Long Amount"] = min(investment_df.loc[i+1, "Long Amount"], investment_df.loc[i+1, "max_long_amt"])
            investment_df.loc[i+1, "marginal_pnl"] = investment_df.loc[i+1, "Long Amount"] * (investment_df.loc[i+1, "Close price"] - investment_df.loc[i+1, "Open price"])
            investment_df.loc[i+1, "commission"] = commission_rate * investment_df.loc[i+1, "Long Amount"] * (investment_df.loc[i+1, "Close price"] + investment_df.loc[i+1, "Open price"])
            investment_df.loc[i+1, "cumulative_pnl"] = investment_df.loc[i, "cumulative_pnl"] + investment_df.loc[i+1, "marginal_pnl"] - investment_df.loc[i+1, "commission"]
                
        return investment_df
    
    def visualize_pnl(self, pnl_df: pd.DataFrame, color1="blue", color2="orange", test=False):
        # 숫자를 K, M, B로 포매팅하는 헬퍼 함수 정의
        def format_large_number(x, pos):
            """
            x: y축 값
            pos: tick 위치(사용하지 않아도 됨)
            """
            if abs(x) >= 1e9:    # 10억(B) 이상
                return f'{x / 1e9:.1f}B'
            elif abs(x) >= 1e6:  # 100만(M) 이상
                return f'{x / 1e6:.1f}M'
            elif abs(x) >= 1e3:  # 1000(K) 이상
                return f'{x / 1e3:.1f}K'
            else:
                return f'{x:.1f}'

        # Figure 및 크기 설정
        plt.figure(figsize=(14, 7))
        
                    # PnL 그래프
        plt.plot(
            pnl_df.loc[:int(len(pnl_df) * 0.8),"Kline open time"], 
            pnl_df.loc[:int(len(pnl_df) * 0.8),"cumulative_pnl"], 
            label="Train Period Cumulative PnL", 
            color=color1, 
            linewidth=2
        )

        if test:
            # PnL 그래프
            plt.plot(
                pnl_df.loc[int(len(pnl_df) * 0.8):,"Kline open time"], 
                pnl_df.loc[int(len(pnl_df) * 0.8):,"cumulative_pnl"], 
                label="Test Period Cumulative PnL", 
                color=color2, 
                linewidth=2
            )

        # 축 및 레이블 설정
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("PnL (in USD)", fontsize=12)
        plt.title("Cumulative PnL Over Time", fontsize=16)
        plt.xticks(rotation=45)
        plt.legend()

        # y축 포매터 지정 (K, M, B 단위로)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_large_number))

        # 레이아웃 최적화 및 그래프 표시
        plt.tight_layout()
        plt.show()

            