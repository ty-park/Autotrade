import time
import pyupbit
import datetime

access = "IxWfhH2o0Vw2o2fZ2wUEnFpdHHqkVWMGY0Ij4iU6"
secret = "w1xBwvtgkZg3zoQ7TIFR2xkRKrF50YvcxQyjqH1x"

# 로그인
upbit = pyupbit.Upbit(access, secret)



class coin:
    def __init__(self,krwticker,ticker,k,interlocktime,emsellpulse):
        self.krwticker = krwticker
        self.ticker = ticker
        self.k = k
        self.interlocktime = interlocktime
        self.emsellpulse = emsellpulse
        self.buyflag = 0
        self.buyinterlocktime = 0
        print('코인모니터링 시작 : ' + self.ticker)
    
    def get_target_price(self):
        """변동성 돌파 전략으로 매수 목표가 조회"""
        df = pyupbit.get_ohlcv(self.krwticker, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * self.k
        return target_price

    def get_start_time(self):
        """시작 시간 조회"""
        df = pyupbit.get_ohlcv(self.krwticker, interval="day", count=1)
        start_time = df.index[0]
        return start_time

    def get_balance(self):
        """잔고 조회"""
        balances = upbit.get_balances()
        for b in balances:
            if b['currency'] == self.krwticker:
                if b['balance'] is not None:
                    return float(b['balance'])
                else:
                    return 0

    def get_current_price(self):
        """현재가 조회"""
        return pyupbit.get_orderbook(tickers=self.krwticker)[0]["orderbook_units"][0]["ask_price"]

    def get_emsell_price(self):
        df = pyupbit.get_ohlcv(self.krwticker, interval="day", count=2)
        targetprice = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * self.k
        highprice = df.iloc[1]['high']
        emsell_price = targetprice+((highprice-targetprice)*0.3)
        return emsell_price
    
    def screening(self):
        try:
            now = datetime.datetime.now()
            start_time = self.get_start_time(self.krwticker)
            end_time = start_time + datetime.timedelta(days=1)
            if self.buyflag==1:
                if self.buyinterlocktime < datetime.datetime.now():
                    emsellprice=self.get_emsell_price(self.krwticker, 0.5)
                    if emsellprice >= self.get_current_price(self.krwticker):
                        upbit.sell_market_order(self.krwticker, self.get_balance(self.ticker))
                        now = datetime.datetime.now()
                        emsleep = ((end_time.hour-now.hour)*60*60)+((end_time.minute-now.minute)*60)+(end_time.second-now.second)-datetime.timedelta(seconds=10)
                        time.sleep(emsleep)              
                        self.buyflag = 0
            elif start_time < now < end_time - datetime.timedelta(seconds=10) :
                target_price = self.get_target_price(self.krwticker, self.k)
                current_price = self.get_current_price(self.krwticker)
                if target_price < current_price:
                    if target_price*1.1 >current_price:
                        krw = self.get_balance("KRW")
                        if krw > 5000:
                            upbit.buy_market_order(self.krwticker, krw)
                            self.buyflag=1
                            self.buyinterlocktime=datetime.datetime.now()+datetime.timedelta(minutes=self.interlocktime)
            else:
                coin = self.get_balance(self.ticker)
                if coin > 0.00008:
                    upbit.sell_market_order(self.krwticker, coin)
            time.sleep(1)

        except Exception as e:
            print(e)
        time.sleep(1)

BTC = coin('KRW-BTC','BTC',0.5,120,0.2)
DOGE = coin('KRW-DOGE','DOGE',0.3,45,0.2)
XRP = coin('KRW-XRP','XRP',0.5,120,0.2)
ETH = coin('KRW-ETH','ETH',0.5,120,0.2)
ETC = coin('KRW-ETC','ETC',0.5,120,0.2)


while True :
    BTC.screening()
    DOGE.screening()
    XRP.screening()
    ETH.screening()
    ETC.screening()
    

