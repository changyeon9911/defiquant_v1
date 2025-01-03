import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from .BacktestManager import BacktestManager
from external_api.exchange.upbit import UpbitInterface

class UpbitBacktestManager(BacktestManager):
    """
    UpbitBacktestManager Class Has Responsibility for:
        - Retrieve Upbit Statistics 
        - Retrieve Buy/Sell Orders
        - Execute Buy/Sell Orders Backtest with Upbit Data
    """
    CANDLESTICK_SYMBOL = "ETH-USDT"
    CANDLESTICK_INTERVAL = "minutes"
    CANDLESTICK_COUNT = 200
    CANDLESTICK_COLS = ["market", "candle_date_time_utc", "candle_date_time_kst", "opening_price", "high_price", "low_price", "trade_price", "timestamp", "candle_acc_trade_price", "candle_acc_trade_volume", "unit"]

    def __init__(self):
        super().__init__()
        
        #AUTH
        load_dotenv()
        UPBIT_API_ACCESS_KEY = os.environ.get("UPBIT_API_ACCESS_KEY")
        UPBIT_API_SECRET_KEY = os.environ.get("UPBIT_API_SECRET_KEY")
        self.interface = UpbitInterface(UPBIT_API_ACCESS_KEY, UPBIT_API_SECRET_KEY)
        
    def load_params(self, params : dict = None):
        tz = ZoneInfo("UTC")
        now = datetime.now(tz)
        to_str = now.isoformat(timespec='seconds')
        if params is None:
            self.params = {"symbol" : self.CANDLESTICK_SYMBOL, "to" : to_str, "count" : self.CANDLESTICK_COUNT}
        else:
            self.params = {"symbol" : self.CANDLESTICK_SYMBOL, "to" : to_str, "count" : self.CANDLESTICK_COUNT}
            for key in params.keys():
                self.params[key] = params[key]
    
    def get_userdata(self):
        userdata = self.interface.get_userdata();
        return userdata

    def get_candlestick(self):
        #datetime columns
        candlestick_df = pd.DataFrame(self.interface.get_candlestick(self.params).json(), columns=self.CANDLESTICK_COLS)
        candlestick_df["candle_date_time_utc"] = pd.to_datetime(candlestick_df["candle_date_time_utc"], unit='us', utc=True).dt.tz_convert("Asia/Seoul")

        #numeric columns
        numeric_columns = [col for col in list(set(candlestick_df.columns) - set({"market", "candle_date_time_utc", "candle_date_time_kst", "unit"}))]
        candlestick_df[numeric_columns] = candlestick_df[numeric_columns].astype("float64")
        candlestick_df["unit"] = candlestick_df["unit"].astype("int64")

        return candlestick_df
    
    def backtest(self, starting_krw, investment_df : pd.DataFrame, commission_rate=0.01):
        investment_df["max_long_amt"] = 0
        investment_df["cumulative_pnl"] = 0
        investment_df.loc[0, "cumulative_pnl"] = starting_krw

        for i in range(len(investment_df)-1):
            investment_df.loc[i, "max_long_amt"] = (investment_df.loc[i, "cumulative_pnl"]/(1+commission_rate))/investment_df.loc[i, "opening_price"]
            investment_df.loc[i, "Long Amount"] = min(investment_df.loc[i, "Long Amount"], investment_df.loc[i, "max_long_amt"])
            investment_df.loc[i, "marginal pnl"] = investment_df.loc[i, "Long Amount"] * (investment_df.loc[i, "trade_price"] - investment_df.loc[i, "opening_price"])
            investment_df.loc[i+1, "cumulative_pnl"] = investment_df.loc[i, "cumulative_pnl"] + investment_df.loc[i, "marginal pnl"]
        
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
            pnl_df.loc[:int(len(pnl_df) * 0.8),"candle_date_time_utc"], 
            pnl_df.loc[:int(len(pnl_df) * 0.8),"cumulative_pnl"], 
            label="Train Period Cumulative PnL", 
            color=color1, 
            linewidth=2
        )

        if test:
            # PnL 그래프
            plt.plot(
                pnl_df.loc[int(len(pnl_df) * 0.8):,"candle_date_time_utc"], 
                pnl_df.loc[int(len(pnl_df) * 0.8):,"cumulative_pnl"], 
                label="Test Period Cumulative PnL", 
                color=color2, 
                linewidth=2
            )

        # 축 및 레이블 설정
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("PnL (in KRW)", fontsize=12)
        plt.title("Cumulative PnL Over Time", fontsize=16)
        plt.xticks(rotation=45)
        plt.legend()

        # y축 포매터 지정 (K, M, B 단위로)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_large_number))

        # 레이아웃 최적화 및 그래프 표시
        plt.tight_layout()
        plt.show()

            