#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
指数日行情
tushare learning: https://tushare.pro/document/1?doc_id=131
https://tushare.pro/document/2?doc_id=128
Created on 2020-02-23
@author: lizhenkun
@contact: 1292746975@qq.com
"""


import tushare as ts

MY_TOKEN = '190040a13eb5b092ca76fa003f58d693c9121e0fc621f6d2ad221468'
# 上证综指
ts_code = '000001.SH'

ts.set_token(MY_TOKEN)
pro = ts.pro_api()
df = pro.index_daily(ts_code=ts_code, start_date='20200217', end_date='20200221')
print(df)