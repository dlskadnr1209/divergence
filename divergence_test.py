from cmath import nan
import ccxt
import pprint
import pandas as pd
from datetime import datetime

import numpy as np
from time import time
from time import localtime, strftime
import time as Tm

def check_diverge(t):
    low_p = price(itv=t)[3]
    high_p = price(itv=t)[2]
    time_p = price(itv=t)[0]
    open_p = price(itv=t)[1] #시가
    close_p = price(itv=t)[4] # 종가
    candle = np.zeros(1000)
    for i in range(1000):
        if close_p[i]-open_p[i] > 0:
            candle[i] = 1 # 양봉
        elif close_p[i]-open_p[i] <0:
            candle[i] = -1 # 음봉
    RSI_cal = rsi_binance(itv=t)
    
    piv_len = 30
    
    if t == '15m':
        price_len = 200
    if t == '1h':
        price_len = 150
    if t == '4h':
        price_len = 100
    
    # 상승 다이버전스 (최솟값)        
    if candle[data_len-4]==-1 and min(low_p[data_len-piv_len:data_len-1]) == low_p[data_len-4] and 30 > min(RSI_cal[data_len-piv_len:data_len-1]) != RSI_cal[data_len-4]:
        val = 1
    
    # 하락 다이버전스 (최댓값)
    elif candle[data_len-4]==1 and max(high_p[data_len-piv_len:data_len-1]) == high_p[data_len-4] and 70 < max(RSI_cal[data_len-piv_len:data_len-1]) != RSI_cal[data_len-4]:
        val = -1
    
    else:
        val = 0

    if val ==1:
        if min(RSI_cal[data_len-piv_len:data_len-1])==RSI_cal[data_len-3] or min(RSI_cal[data_len-piv_len:data_len-1])==RSI_cal[data_len-2]:
            val=0
    if val ==-1:
        if max(RSI_cal[data_len-piv_len:data_len-1])== RSI_cal[data_len-3] or max(RSI_cal[data_len-piv_len:data_len-1])== RSI_cal[data_len-2]:
            val=0
                
    return val
def short_coin(r):
    print("숏", r)
    
def long_coin(r):
    print("롱", r)

def check_rsi(t, n):
    rsi_ = rsi_binance(itv=t)
    rsi = rsi_[998]
#    print(rsi)
    if rsi < n:
        val = 1
    elif rsi > n:
        val = -1
    else:
        val = 0
    return val

def end_position(ls, t):
    if ls < 0: # 숏이면 ?
        ck_rsi = check_rsi(t, 40)
        if ck_rsi == 1:
            short_coin("익절")
            val = 1

        else:
            val = 0
    else:   # 롱이면 ? 
        ck_rsi = check_rsi(t, 60)
        if ck_rsi == -1:
            long_coin("익절")
            val = 1

        else:
            val = 0
    return val

def fin_position(ls, t):
    if t == 'siren':
        if ls < 0:
            short_coin("로스컷")
            val = 1

        elif ls > 0:
            long_coin("로스컷")
            val = 1

    else:
        if ls < 0: # 숏이면 ?
            ck_rsi = check_rsi(t, 25)
            ck_div = check_diverge(t)
            if ck_rsi == 1 or ck_div == 1:
                short_coin("모든포지션정리")
                val = 1

            else:
                val = 0
        else:   # 롱이면 ? 
            ck_rsi = check_rsi(t, 75)
            ck_div = check_diverge(t)
            if ck_rsi == -1 or  ck_div == -1:
                long_coin("모든포지션정리")
                val = 1

            else:
                val = 0
    return val

def rsi_calc(ohlc: pd.DataFrame, period: int = 14):
        ohlc = ohlc[4].astype(float)
        delta = ohlc.diff()
        gains, declines = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        declines[declines > 0] = 0

        _gain = gains.ewm(com=(period-1), min_periods=period).mean()
        _loss = declines.abs().ewm(com=(period-1), min_periods=period).mean()
    
        RS = _gain / _loss
        return pd.Series(100-(100/(1+RS)), name="RSI")

def rsi_binance(itv='1h', simbol='BTC/USDT'):
    binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})
    time_format = '%Y-%m-%d %H:%M:%S'
    day = strftime(time_format, tm)
    ref_time = round(datetime.strptime(str(day), '%Y-%m-%d %H:%M:%S').timestamp()*1000)
    
    if itv == '4h':
        ref_time -= 1000 * 4 * 3600 * (data_len-1)
    elif itv == '1h':
        ref_time -= 1000 * 3600 * (data_len-1)
    elif itv == '15m':
        ref_time -= 1000 * 60 * 15 * (data_len-1)
    elif itv == '1m':
        ref_time -= 1000 * 60 * (data_len-1)
            
    ohlcv = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe=itv, since=ref_time, limit=data_len)
    df = pd.DataFrame(ohlcv)
    # rsi = rsi_calc(df,14).iloc[-1] # 마지막 RSI
    rsi = rsi_calc(df,14) # RSI 14
    return rsi

def price(itv, simbol='BTC/USDT'): # time, open, high, low, close, vol
    binance = ccxt.binance()
    time_format = '%Y-%m-%d %H:%M:%S'
    day = strftime(time_format, tm)
    ref_time = round(datetime.strptime(str(day), '%Y-%m-%d %H:%M:%S').timestamp()*1000)
    
    if itv == '4h':
        ref_time -= 1000 * 4 * 3600 * (data_len-1)
    elif itv == '1h':
        ref_time -= 1000 * 3600 * (data_len-1)
    elif itv == '15m':
        ref_time -= 1000 * 60 * 15 * (data_len-1)
    elif itv == '1m':
        ref_time -= 1000 * 60 * (data_len-1)
    
    ohlcv = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe=itv, since=ref_time, limit=data_len)
    df = pd.DataFrame(ohlcv)
    return df

trig = 1
sl = 0
entry_price = 0
now_position = 0
data_len = 1000
USDT = 100
leverage = 10
ls = 0
i=0
api_key = ""
api_secret = ""

backtest_time = 1649637001
# tm = localtime(1649637016.7605205) # 백테스트용
tm = localtime(backtest_time)
hour = tm.tm_hour
minute = tm.tm_min
print(tm.tm_year, "  ", tm.tm_mon, "  ", tm.tm_mday, "  ", tm.tm_hour, "  ", tm.tm_min)
while True: # 진짜 트레이딩 때
# for kpkp in range(15):
    USDT_temp = USDT
    # tm = localtime(time())
    tm = localtime(backtest_time)
    hour = tm.tm_hour
    minute = tm.tm_min
    
    if trig == 1: # 무포지션
    
        ratio = 0
        long_or_short = 0

        if minute % 15 == 0: # 15분 다이버전스
            t = '15m'
            ls = check_diverge(t)
            if ls != 0:
                ratio = 20
                print("15m 다이버전스")
            long_or_short += ls
            
        if minute == 00: # 1시간 다이버전스
            t = '1h'
            ls = check_diverge(t)
            if ls != 0:
                ratio = 25
                print("1h 다이버전스")
            long_or_short += ls
            
        if hour % 4 == 1 and minute == 0: # 4시간 다이버전스
            t = '4h'
            ls = check_diverge(t)
            if ls != 0:
                ratio = 30
                print("4h 다이버전스")
            long_or_short += ls
                                    
        if ratio == 20:
            trading_interval = '15m'
        elif ratio == 25:
           trading_interval = '1h'
        elif ratio == 30:
            trading_interval = '4h'
        
        if long_or_short < 0: # 숏 + 포지션 잡았다고 트리거
            # for backtest
            now_position = USDT * ratio / 100 * leverage # 현재 포지션 총 달러
            USDT -= USDT * ratio / 100
            now_price = price(itv=trading_interval)[1]
            entry_price = now_price[999]
            
            high_price = price(itv=trading_interval)[2]
            sl = high_price[996]
            short_coin(r=entry_price)   
            trig = 0
            print("now_position" , now_position)
        elif long_or_short > 0: # 롱 + 포지션 잡았다고 트리거
            # for backtest
            now_position = USDT * ratio / 100 * leverage# 현재 포지션 총 달러
            USDT -= USDT * ratio / 100
            now_price = price(itv=trading_interval)[1]
            entry_price = now_price[999]
            low_price = price(itv=trading_interval)[3]
            sl = low_price[996]
            long_coin(r=entry_price)
            trig = 0
            print("now_position" , now_position)
    elif trig == 0: # 포지션 있음
        # setting stop loss # 손절라인 정하기
        if ratio == 20:
            ep = end_position(long_or_short, '15m') # 팔았냐 / 안팔았냐
            
        elif ratio == 25:
            ep = end_position(long_or_short, '1h') # 팔았냐 / 안팔았냐
            
        elif ratio == 30:
            ep = end_position(long_or_short, '4h') # 팔았냐 / 안팔았냐
        
        if ep == 1: # 팔았으면 
            # for backtest
            now_price = price(itv=trading_interval)[1]
            tp = now_price[999]
            print("현재가격",tp)
            if tp > entry_price: # 롱 익절
                USDT = USDT + now_position/2/leverage + now_position / 2 * (tp - entry_price) / entry_price
            elif tp < entry_price: # 숏 익절
                USDT = USDT + now_position/2/leverage + now_position / 2 * (entry_price - tp) / entry_price

            now_position = now_position / 2
            trig = 2 # 한 번 팔았음
            sl = entry_price # 스탑로스 본절
            print("now_position" , now_position)
            print(USDT)
    elif trig == 2: # 한 번 판 후
        if ratio == 20:
            fp = fin_position(long_or_short, '15m') # 팔았냐 / 안팔았냐
            
        elif ratio == 25:
            fp = fin_position(long_or_short, '1h') # 팔았냐 / 안팔았냐
            
        elif ratio == 30:
            fp = fin_position(long_or_short, '4h') # 팔았냐 / 안팔았냐
        
        if fp == 1: # 팔았으면
            # for backtest
            now_price = price(itv=trading_interval)[1]
            tp = now_price[999]
            print("현재가격",tp)
            if tp > entry_price: # 롱 익절
                USDT = USDT + now_position/leverage + now_position * (tp - entry_price) / entry_price
            elif tp < entry_price: # 숏 익절
                USDT = USDT + now_position/leverage + now_position * (entry_price - tp) / entry_price
            
            now_position = 0
            long_or_short = 0
            trig = 1 # 다시 무포지션
            sl = 0
            print(USDT)
        
    # if trig == 1 and hour == 9 and minute == 00: # 시간 밀리는 거 체크 / 아침 9시에 끝
    #     break
    
    Tm.sleep(10) # 1분 마다 루프
    now_price = price(itv='1m')[1]
    price_time = now_price[999]

    if trig != 1 and long_or_short > 0 and price_time < sl: # 롱일 때 손절
        fin_position(long_or_short, 'siren')
        # for backtest
        tp = price_time
        print("현재가격",tp)
        USDT = USDT + now_position/leverage - now_position * (entry_price - tp) / entry_price
        trig=1
        sl = 0
        long_or_short = 0
        now_position = 0
        print(USDT)
    elif trig != 1 and long_or_short < 0 and price_time > sl: # 숏일 때 손절
        fin_position(long_or_short, 'siren')
        # for backtest
        tp = price_time
        print("현재가격",tp)
        USDT = USDT + now_position/leverage - now_position * (tp - entry_price) / entry_price
        trig=1
        sl = 0
        long_or_short = 0
        now_position = 0
        print(USDT)
    backtest_time = backtest_time + 900
    i+=1
    print_time = localtime(backtest_time)
    
#    if print_time.tm_min % 5 == 1:
#        print(print_time.tm_year, "  ", print_time.tm_mon, "  ", print_time.tm_mday, "  ", print_time.tm_hour, "  ", print_time.tm_min)
    
#    if USDT_temp != USDT:
#        print(USDT)
    
    if i % 30==0:
        print_time = localtime(backtest_time)
        print(print_time.tm_year, "  ", print_time.tm_mon, "  ", print_time.tm_mday, "  ", print_time.tm_hour, "  ", print_time.tm_min)
