#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
股票日行情
tushare learning: https://tushare.pro/document/1?doc_id=131
Created on 2020-02-23
@author: lizhenkun
@contact: 1292746975@qq.com
"""
import os
import pandas as pd
import tushare as ts
from datetime import datetime

MY_TOKEN = '190040a13eb5b092ca76fa003f58d693c9121e0fc621f6d2ad221468'
ts_code='002713.SZ'
csv_file = '{0}.csv'.format(ts_code)
begin_date = '20140101'
end_date = datetime.now().strftime('%Y%m%d')

ts.set_token(MY_TOKEN)
pro = ts.pro_api()
# 获取前复权数据
df = pro.daily(ts_code=ts_code, adj='qfq', start_date=begin_date, end_date=end_date)
df.to_csv(csv_file, index=False)
# print(df)
# df = df1.sort_values(by=['trade_date'])
# df.reset_index(level=0, inplace=True)
# df.drop(['index', 'ts_code'], axis=1, inplace=True)
# print(df)
# df.to_csv(csv_file)

# period_df.reset_index(inplace=True)
# df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]


