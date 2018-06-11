#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 03:01:45 2018
PULL WULL OFF SHEEP
@author: chenmengyuan
"""

#from fcoin import Fcoin
import time
from decimal import *
import numpy as np
import pandas as pd
import talib
#if python3 use fcoin3
from fcoin3 import Fcoin

pair = 'ftbtc'
fee = 0.001
fcoin = Fcoin()
fcoin.proxies = {
    'http': 'http://127.0.0.1:8123',
    'https': 'http://127.0.0.1:8123',
    }
fcoin.auth('key', 'secret') 
orders = []
hold = 0 #持仓
def main():
    lastBar = 0
    count = 0
    buy = sell = []
    vol = 10#默认持仓
    actions = []#操作记录
    hold = 0
    #print(fcoin.get_symbols())
#    balance = fcoin.get_balance()
#    print(balance)
    
#    
#    #vol = (lambda a,b: 10 if min(a, b) > 10 else min(a, b))(dib_vol, ask_vol)
#    print('买入:', bid, ';卖出', ask, ';数量', vol)
##    print('买单：', fcoin.buy(pair, bid, vol))
##    print('卖单：', fcoin.sell(pair, ask, vol * (1-fee)))
##    
##    orders = fcoin.list_orders()
##    print(orders)
#    balance = fcoin.get_balance()
#    balances = []
#    for data in balance['data']:
#        temp = []
#        for j in data:
#            temp.append(data[j])
#        if Decimal(temp[0]) != 0:
#            balances.append(temp)
#    print(balances)
    while(1):
        ohlcv = getOHLCV()
        ohlcv = ohlcv.sort_index(by='time')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time))))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.tail(1).time))))
        dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        
        print(bar.tail(10))
        curBar = bar[0]
        if bar[0] * bar[1] < 0:
            if bar[0] < 0 and bar[1] > 0  and hold > 0:
                orders.append(sell())
            if bar[0] > 0 and bar[1] < 0:
                orders.append(buy())
        while(len(orders) > 0):
            order = fcoin.get_order(orders[0])['data']
            state = order['state']
            dire = order['side']
            if state == 'filled':
                if dire == 'sell':
                    hold = 0
                else:
                    hold = order['filled_amount']
                orders.pop()
            time.sleep(1)
        print('当前持仓', getBalance())
        print('当前hold', hold)
        time.sleep(30)

def getOHLCV():
    datas = fcoin.get_candle('M1',pair)
    ohlcv = []
    for data in datas['data']:
        ohlcv.append([data['id'], data['open'], data['high'], data['low'], data['close'], data['quote_vol']])
        
    ohlcv = pd.DataFrame(np.array(ohlcv), columns=('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    return ohlcv

def getPrice():
    depth = fcoin.get_market_depth('L20', pair)
    #print(depth)
    bid = depth['data']['bids'][0]
    ask = depth['data']['asks'][0]
    return ask, bid

def getBalance():
    getBala = fcoin.get_balance()
    balances = []
    for data in getBala['data']:
        if Decimal(data['balance']) != 0:
            balances.append([data['balance'], data['available'], data['currency'], data['frozen']])
    #print(balances)
    return balances

def sell():
    ask, bid = getPrice()
    amount = getBalance()[1][1]
    round(float(amount) / ask, 2)
    timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    ask = str(round(Decimal(ask), 8))
    print(timeNow, '创建卖单，卖价', ask, '数量：', amount)
    order = fcoin.sell(pair, ask, amount)
    if order.shape <= 0:
        print('创建买单失败')
        return []
    return order['data']

def buy():
    ask, bid = getPrice()
    amount = getBalance()[0][1]
    amount = round(float(amount) / bid, 2)
    timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    bid = str(round(Decimal(bid), 8))
    print(timeNow, '创建买单，买价', bid, '数量：', amount)
    order = fcoin.buy(pair, bid, amount)
    if order.shape <= 0:
        print('创建买单失败')
        return []
    return order['data']

if __name__ == '__main__':
    main()
    