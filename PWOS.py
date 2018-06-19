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
today = time.strftime('%Y%m%d', time.localtime(time.time()))
logger = logging.getLogger('mylogger') 
logger.setLevel(logging.DEBUG) 
   
fh = logging.FileHandler('PWOS_'+today+'.log') 
fh.setLevel(logging.DEBUG) 
ch = logging.StreamHandler() 
ch.setLevel(logging.DEBUG) 
formatter = logging.Formatter('[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s')
fh.setFormatter(formatter) 
ch.setFormatter(formatter) 
logger.addHandler(fh) 
logger.addHandler(ch) 
#logger.info('foorbar') 

odlogger = logging.getLogger('mylogger')
odlogger.setLevel(logging.DEBUG)
th = logging.FileHandler('order.log') 
th.setLevel(logging.DEBUG) 
odlogger.addHandler(th) 

def main():
    buy = sell = []
    while(1):
        #today = time.strftime('%Y%m%d', time.localtime(time.time()))
        #fh = logging.FileHandler('PWOS_'+today+'.log') 
        gB = getBalance()
        hold = round(float(gB[1][1]), 2)
        ohlcv = getOHLCV()
        ohlcv = ohlcv.sort_index(by='time')
        logger.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time))))
        logger.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.tail(1).time))))
        dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        #BTC+FT
        logger.info('BALANCE NOW')
        logger.info(gB)
        logger.info('hold:')
        logger.info(hold)
        logger.info('Balance(BTC)')
        balBTC = float(gB[0][0]) + float(gB[1][0]) * float(ohlcv.tail(1).close)
        logger.info(balBTC)
        logger.info(ohlcv.tail(5))
        logger.info(bar.tail(10))
        logger.info('dif[0]')
        logger.info(dif[0])
        orders = []
        t10 = bar.tail(10)
        #TODO:emmmmmmmmm if True:
        #At least last 2 bars with same sign to get rid of interfering data
        #if((sum(t10 > 0) < 10 and sum(t10 > 0) > 0) or sum(t10 > 0) == 10 or sum(t10 > 0) == 0):
        if(sum(t10 > 0) <= 10 and sum(t10 > 0) > 0):
            if bar[0] < 0 and bar[1] < 0 and hold > 1:
                res = sellAct()
                if float(res) > 0:
                    #hold -= res
                    pass
            if bar[0] > 0 and bar[1] > 0 and dif[0] > 0 and hold <= 1:
                res = buyAct()
                if float(res) > 0:
                    #hold += res
                    pass
#        if bar[0] * bar[1] < 0:
#            if bar[0] < 0 and bar[1] > 0  and hold > 1:
#                res = sellAct()
#                if res > 0:
#                    hold = 0
#            if bar[0] > 0 and bar[1] < 0 and hold < 1:
#                res = buyAct()
#                if res > 0:
#                    hold = res
        time.sleep(60)
def getOHLCV():
    datas = fcoin.get_candle('M1',pair)
    ohlcv = []
    for data in datas['data']:
        ohlcv.append([data['id'], data['open'], data['high'], data['low'], data['close'], data['quote_vol']])
    pd.set_option('precision', 8)
    ohlcv = pd.DataFrame(np.array(ohlcv), columns=('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    return ohlcv

def getPrice():
    depth = fcoin.get_market_depth('L20', pair)
    #print(depth)
    bid = depth['data']['bids'][0]
    ask = depth['data']['asks'][0]
    return ask, bid

def getBalance():
    showBalance = ['ft', 'btc']
    getBala = fcoin.get_balance()
    balances = []
    for data in getBala['data']:
        #if Decimal(data['balance']) != 0:
        for t in showBalance:
            if data['currency'] == t:
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
        if amount <= 1:
            logger.info('Without enough number!')
            return -1
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
                logger.info('Order filled!')
                odlogger.info(order)
                return float(order['filled_amount'])
            time.sleep(1)
            count += 1
        logger.info('cancel sell order')
        rec = fcoin.cancel_order(order['id'])
        logger.info(rec)
        if len(rec) > 0 and rec['status'] == 0:
            logger.info('Cancel sell order!')
        else :
            logger.error(order)
            logger.error('Cancel FAILED!')
            return -1
        logger.info(order)
        logger.info('Sell failure. Recreate the order!')
        #time.sleep(2)
        #while(fcoin.get_order(orderId)['data']['state'].find('canceled') == -1):
        #    time.sleep(1)
    

def buyAct():
    while(1):
        ask, bid = getPrice()
        amount = getBalance()[0][1]
        amount = floor(round(float(amount) / bid, 2))
        timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        bid = str(round(Decimal(bid), 8))
        logger.info('Create Order:===>buy')
        logger.info('buy_price')
        logger.info(bid)
        logger.info('amount:')
        logger.info(amount)
        if amount <= 0.001:
            logger.info('Without enough number!')
            return -1
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
                logger.info('Order filled!')
                odlogger.info(order)
                return float(order['filled_amount'])
            time.sleep(1)
            count += 1
        rec = fcoin.cancel_order(order['id'])
        logger.info(rec)
        if len(rec) > 0 and rec['status'] == 0:
            logger.info('Cancel buy order!')
        else :
            logger.error(order)
            logger.error('Cancel FAILED!')
            return -1
        logger.info(order)
        logger.info('Buy failure. Recreate the order!')
        #time.sleep(2)
        #while(fcoin.get_order(orderId)['data']['state'].find('canceled') == -1):
        #    time.sleep(1)

if __name__ == '__main__':
    main()
    
