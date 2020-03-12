
# coding=utf-8
'''
stock service implements by pytdx
Created on 2020-03-01
@author: lizhenkun
@contact: 1292746975@qq.com
'''
if not __package__:
    import _sys_path_append_

import os
import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame

import src.lib.constants as ct
import src.conf.accounts as accounts

from pytdx.hq import TdxHq_API

FREQUENT = {
    '1min': 7,
    '5min': 0,
    '15min': 1,
    '30min': 2,
    '60min': 3,
    'day': 4,
    'week': 5,
    'month': 6,
    'season': 10,
    'year': 11
}

def download_history_fq_data(stock_code, fq_type='qfq', kline_type='day'):
    api_url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={param}'
    if stock_code[0] == '0':
        stock_code = 'sz' + stock_code
    else:
        stock_code = 'sh' + stock_code

    # _var = 'kline_{kl_type}{fq_type}'
    year = int(datetime.now().strftime('%Y'))
    headers = ['datetime', 'open', 'close', 'high', 'low', 'amount', 'xdxrinfo']
    stock_data = []
    while True:
        start_date = '{year}-01-01'.format(year=year)
        end_date = '{year}-12-31'.format(year=year)
    
        param = '{code},{kline_type},{start_date},{end_date},640,{fq_type}'.format(
            code=stock_code, kline_type=kline_type,
            start_date=start_date, end_date=end_date, fq_type=fq_type
        )
        request_url = api_url.format(param=param)
        resp = requests.get(request_url)
        data = json.loads(resp.text)
        qfqday_data = data['data'][stock_code].get('qfqday')
        if qfqday_data:
            stock_data.extend(qfqday_data)
            print(year, start_date, end_date, qfqday_data[0], qfqday_data[-1])
        else:
            break
        
        year -= 1
    print(stock_data[0], stock_data[1])
    stock_df = pd.DataFrame(stock_data, columns=headers)
    stock_df = stock_df[['datetime', 'open', 'high', 'low', 'close', 'amount']
        ].sort_values(by=['datetime']).reset_index(drop=True)
    print(stock_df)
    return stock_df


def download_history_data(stock_code, frequent):
    if stock_code[0] == '0':
        market = 0
    else:
        market = 1
    category = FREQUENT[frequent]

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        index = 0
        stock_data = []
        while True:
            older_data = api.get_security_bars(category, market, stock_code, index * 800, 800)
            if older_data:
                stock_data = older_data + stock_data
                index += 1
            else:
                break
        stock_df = api.to_df(stock_data) # 返回DataFrame
    return stock_df[ct.STOCK_COLS]


def get_xdxr_info(stock_code, market):
    api = TdxHq_API()
    xdxr_df = None
    with api.connect('119.147.212.81', 7709):
        xdxr_df = api.get_xdxr_info(market, stock_code)
        xdxr_df = api.to_df(xdxr_df)
        
    return xdxr_df


if __name__ == "__main__":
    stock_code = '000723'
    download_history_fq_data(stock_code)

    # market = 0
    # xdxr_df = get_xdxr_info(stock_code, market)
    # xdxr_df['datetime'] = (xdxr_df['year'].map(str) + '-' +
    #     xdxr_df['month'].map(str)  + '-' + xdxr_df['day'].map(str))
    # xdxr_df['datetime'] = pd.to_datetime(xdxr_df['datetime'])
    # xdxr_df.drop(['year', 'month', 'day'], axis=1, inplace=True)
    # # xdxr_df = xdxr_df[xdxr_df['category'] == 1]
    # xdxr_df.reset_index(inplace=True, drop=True)
    # print(xdxr_df)
    # xdxr_df.to_csv('%s_xdxr.csv' % stock_code)

    # xdxr_df = xdxr_df[xdxr_df['category'] == 1]
    # print(xdxr_df)

    # stock_df = pd.read_csv('/Users/lizhenkun01/workspace/GitHub/quant-trade-learning/data/china/stock/000723_day_1997-05-15 15:00_2020-03-06 15:00.csv')
    # print(stock_df)