
# coding=utf-8
'''
腾讯接口
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


def download_data(stock_code, freq='day', fq_type='qfq', last_time=None):
    # year = int(datetime.now().strftime('%Y'))
    now = datetime.now()
    if last_time:
        if freq.find('min') != -1:
            last_date = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        else:
            last_date = datetime.strptime(last_time, '%Y-%m-%d')


def download_stock_bars(stock_code, freq='day', fq_type='qfq'):
    api_url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={param}'
    if stock_code[0] == '0':
        stock_code = 'sz' + stock_code
    else:
        stock_code = 'sh' + stock_code

    year = int(datetime.now().strftime('%Y'))
    headers = ['datetime', 'open', 'close', 'high', 'low', 'amount', 'xdxrinfo']
    stock_data = []
    while True:
        start_date = '{year}-01-01'.format(year=year)
        end_date = '{year}-12-31'.format(year=year)
    
        param = '{code},{freq},{start_date},{end_date},640,{fq_type}'.format(
            code=stock_code, freq=freq,
            start_date=start_date, end_date=end_date, fq_type=fq_type
        )
        request_url = api_url.format(param=param)
        print(request_url)
        resp = requests.get(request_url)
        data = json.loads(resp.text)
        qfqday_data = data['data'][stock_code].get('qfqday')
        if qfqday_data:
            stock_data.extend(qfqday_data)
            print(year, start_date, end_date, qfqday_data[0], qfqday_data[-1])
        else:
            break
        
        year -= 1
    stock_df = pd.DataFrame(stock_data, columns=headers)
    stock_df = stock_df[['datetime', 'open', 'high', 'low', 'close', 'amount']
        ].sort_values(by=['datetime']).reset_index(drop=True)
    print(stock_df)
    return stock_df



if __name__ == "__main__":
    stock_code = '000723'
    download_history_fq_data(stock_code)
