# coding=utf-8
"""
股票日行情
tushare learning: https://tushare.pro/document/1?doc_id=131
Created on 2020-02-23
@author: lizhenkun
@contact: 1292746975@qq.com
"""
import os
import pandas as pd

ts_code='002713.SZ'
csv_file = '{0}.csv'.format(ts_code)
reorg_file = 'reorg_{0}.csv'.format(ts_code)
# print(df)
df = pd.read_csv(csv_file)
df = df[['trade_date', 'open', 'high', 'low', 'close', 'change']]
df.sort_values(by=['trade_date'], inplace=True)
df.reset_index(0, drop=True, inplace=True)
# 根据收盘价计算涨跌幅
df['change'] = df['close'].pct_change(1)
df.to_csv(reorg_file, index=False)
print(df)
# df = pd.read_csv(reorg_file)
# print(df)

