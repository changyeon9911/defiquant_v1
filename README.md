# 목표

---

- Token Trading Bot 만들기
    - 구현조건
        1. Binance 내에서만 거래
        2. 공매도는 고려하지 않음
        3. Spot-Trading만 대상으로 함
        4. 거래 수수료 고려하지 않음
    - 프로그래밍 스타일
        - Agile
        - 객체지향적 프로그래밍 사용하기

# 로드맵

---

## 1. 개발 환경 설정

- Docker 이미지 선택
    - 개발 스택: Python

## 2. 구현사항 정리

- API 인터페이스
    - 바이낸스 API 인터페이스 클래스
- 리서치 클래스
    - 백테스팅 함수
        - 이번 거래의 pnl에 의해 다음번 거래의 booksize가 달라진다는 점을 고려
        - 수수료 고려
    - PnL 시각화
- 전략 클래스
    - Input: 다양한 데이터를 받아서
    - Inner Process: 투자분석을 진행
    - output: 종목별 가중치 산출 반환
- 주문 클래스
    - Input: 종목별 가중치를 받아서
    - Inner Process: 실제 주문 체결
    - output: 주문 결과 반환

## 3. 객체 인터페이스

- API 인터페이스
    - 바이낸스 API 인터페이스 클래스
        - load_params
        - get_statistics_24hr
        - get_candlestick
        - backtest
        - visualize_pnl
        - get_userdata
- 전략 생성 인터페이스
    - 미정..
- 주문 체결 인터페이스
    - retrieve_orders
    - execute_orders

## 4. 백테스팅 예시

```python
#system settings
import sys
sys.path.append("../")

#lib settings
import pandas as pd
from researcher import UpbitBacktestManager
```

```python
# Candlestick loader

def candlestick_loader(base, quote, interval, unit):
    u_mangr = UpbitBacktestManager()
    u_mangr.load_params({"market" : f"{quote}-{base}"})
    candlestick_df = u_mangr.get_candlestick(interval=interval, unit=unit)
    return u_mangr, candlestick_df
```

```python
# Sample Investment Table(strat_bollinger_momentum)

def strat_bollinger_reversion(candlestick_df : pd.DataFrame, window=10):
    investment_df = candlestick_df.copy()[["candle_date_time_utc", "opening_price", "trade_price"]]
    investment_df["Previous trade_price"] = investment_df["trade_price"].shift(1)
    investment_df["std_window"] = investment_df["Previous trade_price"].rolling(window).std()
    investment_df["boll_upper"] = investment_df["Previous trade_price"].rolling(window).mean() + investment_df["std_window"]
    investment_df["boll_lower"] = investment_df["Previous trade_price"].rolling(window).mean() - investment_df["std_window"]
    investment_df["Long Ratio"] = (investment_df["boll_lower"] - investment_df["opening_price"]).div(investment_df["std_window"])
    investment_df["Long Ratio"] = investment_df["Long Ratio"].fillna(0).clip(0)
    return investment_df

def price_momentum(candlestick_df : pd.DataFrame, window=10):
    investment_df = candlestick_df.copy()[["candle_date_time_utc", "opening_price", "trade_price"]]
    investment_df["Previous opening_price"] = investment_df["opening_price"].shift(1)
    investment_df["Long Ratio"] = (investment_df["opening_price"] - investment_df["Previous opening_price"].rolling(window).mean())/investment_df["Previous opening_price"].rolling(window).mean()
    investment_df["Long Ratio"] = investment_df["Long Ratio"].fillna(0).clip(lower=0, upper=1)
    return investment_df

def volume_momentum(candlestick_df : pd.DataFrame, window=10):
    investment_df = candlestick_df.copy()[["candle_date_time_utc", "opening_price", "trade_price", "candle_acc_trade_price"]]
    investment_df["Previous Volume"] = investment_df["candle_acc_trade_price"].shift(1)
    investment_df["Long Ratio"] = (investment_df["candle_acc_trade_price"] - investment_df["Previous Volume"].rolling(window).mean())/investment_df["Previous Volume"].rolling(window).mean()
    investment_df["Long Ratio"] = investment_df["Long Ratio"].fillna(0).clip(lower=0, upper=1)
    return investment_df
```

```python
b_mangr, candlestick_df = candlestick_loader(base="DOGE", quote="KRW", interval=None, unit="days")

# PnL Dataframe
pnl_df_train = b_mangr.backtest(starting_krw=500000, investment_df=volume_momentum(candlestick_df, window=10));

#visualization
b_mangr.visualize_pnl(pnl_df_train, test=True)
```

![image.png](https://github.com/user-attachments/assets/ea891e0b-df7f-4d7b-86e7-309e07af8a3a)