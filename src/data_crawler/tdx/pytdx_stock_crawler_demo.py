# coding=utf-8
'''
stock service implements by pytdx
Created on 2020-03-01
@author: lizhenkun
@contact: 1292746975@qq.com
'''
import os
import pandas as pd
from datetime import datetime

import _sys_path_append_
import src.lib.constants as ct
import src.conf.accounts as accounts

from pytdx.hq import TdxHq_API

stock_code = '002713.SZ'
api = TdxHq_API()
"""
get_security_bars Argusments
category: {
    0: 5分钟
    1: 15分钟
    2: 30分钟
    3: 60分钟 [9:30, 10:30, 11:30, 2, 3]
    4: 日K线
    5: 周K线
    6: 月K线
    7: 1分钟
    8: 1分钟
    9: 日K线
    10: 季K线
    11: 年
},
market: {
    0: 深圳
    1: 上海
}.
code
start: 指定的范围开始位置, 0 代表最近的收盘
count: 请求的K线数目, 最大值为800
"""
with api.connect('119.147.212.81', 7709):
    csv_file = os.path.join(ct.CHINA_STOCK_DATA_DIR, '{0}_5min.csv'.format(stock_code))
    # 省略 api.disconnect()
    # data = api.get_security_bars(9, 0, '000001', 0, 10) #返回普通list
    stock_list = api.get_security_bars(4, 0, '002713', 0, 10)
    
    stock_df = api.to_df(stock_list) # 返回DataFrame
    stock_df.sort_index(ascending=False, inplace=True)
    # print(stock_df[['open', 'high', 'low', 'close', 'vol', 'amount', 'datetime']].to_string())
    print(stock_df.to_string(columns=['open', 'high', 'low', 'close', 'vol', 'amount', 'datetime']))
    with open(csv_file, 'r+') as fio:
        fio.seek(0, 0)
        fio.write(stock_df.to_string(columns=['open', 'high', 'low', 'close', 'vol', 'amount', 'datetime']))
    # if os.path.exists(csv_file):
    #     stock_df.to_csv(csv_file, index=False, mode='a', header=False)
    # else:
    #     stock_df.to_csv(csv_file, index=False)