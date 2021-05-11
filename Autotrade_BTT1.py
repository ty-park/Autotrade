import time
import pyupbit
import datetime

access = "access"          # 본인 값으로 변경
secret = "secret"          # 본인 값으로 변경

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_emsell_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    targetprice = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    highprice = df.iloc[1]['high']
    nprice = pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]
    emsell_price = targetprice+((highprice-targetprice)*0.3)
    return emsell_price

# 로그인
upbit = pyupbit.Upbit(access, secret)
buyflag = 0
buyinterlocktime = 0
print("autotrade start")


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTT")
        end_time = start_time + datetime.timedelta(days=1)
        if buyflag==1:
            if buyinterlocktime < datetime.datetime.now():
                emsellprice=get_emsell_price('KRW-BTT', 0.5)
                if emsellprice >= get_current_price('KRW-BTT'):
                    upbit.sell_market_order('KRW-BTT', get_balance('BTT'))
                    now = datetime.datetime.now()
                    emsleep = ((end_time.hour-now.hour)*60*60)+((end_time.minute-now.minute)*60)+(end_time.second-now.second)-datetime.timedelta(seconds=10)
                    time.sleep(emsleep)              
                    buyflag = 0
        elif start_time < now < end_time - datetime.timedelta(seconds=10) :
            target_price = get_target_price("KRW-BTT", 0.5)
            current_price = get_current_price("KRW-BTT")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTT", krw*0.9995)
                    buyflag=1
                    buyinterlocktime=datetime.datetime.now()+datetime.timedelta(minutes=50)
        else:
            coin = get_balance("BTT")
            if coin > 0.00008:
                upbit.sell_market_order("KRW-BTT", coin)
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)