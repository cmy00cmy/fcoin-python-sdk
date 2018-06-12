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
from math import floor
import logging
import configparser
#if python3 use fcoin3
from fcoin3 import Fcoin

pair = 'ftbtc'
fee = 0.001
fcoin = Fcoin()
fcoin.proxies = {
    'http': 'http://127.0.0.1:8123',
    'https': 'http://127.0.0.1:8123',
    }
conf = configparser.SafeConfigParser()
conf.read('conf.ini')
key = conf.get('fcoin', 'key')
secret = conf.get('fcoin', 'secret')
fcoin.auth(key, secret) 

logger = logging.getLogger('mylogger') 
logger.setLevel(logging.DEBUG) 
   
fh = logging.FileHandler('PWOS.log') 
fh.setLevel(logging.DEBUG) 
ch = logging.StreamHandler() 
ch.setLevel(logging.DEBUG) 
formatter = logging.Formatter('[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s')
fh.setFormatter(formatter) 
ch.setFormatter(formatter) 
logger.addHandler(fh) 
logger.addHandler(ch) 
#logger.info('foorbar') 

def main():
    buy = sell = []
    while(1):
        hold = round(float(getBalance()[1][1]), 2)
        ohlcv = getOHLCV()
        ohlcv = ohlcv.sort_index(by='time')
        logger.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time))))
        logger.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.tail(1).time))))
        dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        
        logger.info(bar.tail(10))
        orders = []
        t10 = bar.tail(10)
        if(sum(t10 > 0) < 10 and sum(t10 > 0) > 0):
            if bar[0] < 0 and hold > 1:
                res = sellAct()
                if res > 0:
                    hold = 0
            if bar[0] > 0 and hold < 1:
                res = buyAct()
                if res > 0:
                    hold = res
#        if bar[0] * bar[1] < 0:
#            if bar[0] < 0 and bar[1] > 0  and hold > 1:
#                res = sellAct()
#                if res > 0:
#                    hold = 0
#            if bar[0] > 0 and bar[1] < 0 and hold < 1:
#                res = buyAct()
#                if res > 0:
#                    hold = res
        
        logger.info('BALANCE NOW')
        logger.info(getBalance())
        logger.info('hold:')
        logger.info(hold)
        time.sleep(60)

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

def sellAct():
    while(1):
        ask, bid = getPrice()
        amount = getBalance()[1][1]
        amount = floor(float(amount))
        timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ask = str(round(Decimal(ask), 8))
        logger.info('Create Order:<===sell')
        logger.info('sell_price')
        logger.info(ask)
        logger.info('amount:')
        logger.info(amount)
        order = fcoin.sell(pair, ask, amount)
        if len(order) <= 0:
            logger.info('CREATE ORDER(SELL) ERROR!!')
            return -1
        orderId = order['data']
        count = 0
        while(count < 10):
            order = fcoin.get_order(orderId)['data']
            state = order['state']
            if state == 'filled':
                return order['filled_amount']
            time.sleep(1)
            count += 1
        print(fcoin.cancel_order(order))
        logger.info('Cancel sell order!')
        logger.info(order)
        logger.info('Sell failure. Recreate the order!')
    

def buyAct():
    while(1):
        ask, bid = getPrice()
        amount = getBalance()[0][1]
        amount = round(float(amount) / bid, 2)
        timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        bid = str(round(Decimal(bid), 8))
        logger.info('Create Order:===>buy')
        logger.info('buy_price')
        logger.info(bid)
        logger.info('amount:')
        logger.info(amount)
        order = fcoin.buy(pair, bid, amount)
        if len(order) <= 0:
            logger.info('CREATE ORDER(BUY) ERROR!!')
            return -1
        orderId = order['data']
        count = 0
        while(count < 10):
            order = fcoin.get_order(orderId)['data']
            state = order['state']
            if state == 'filled':
                return order['filled_amount']
            time.sleep(1)
            count += 1
        print(fcoin.cancel_order(order))
        logger.info('Cancel buy order!')
        logger.info(order)
        logger.info('Buy failure. Recreate the order!')

if __name__ == '__main__':
    main()
    
