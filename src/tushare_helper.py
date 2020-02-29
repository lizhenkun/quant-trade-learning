#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
tushare learning: https://tushare.pro/document/1?doc_id=131
Created on 2020-02-23
@author: lizhenkun
@contact: 1292746975@qq.com
"""
import tushare as ts


class TusahreApi(object):
    MY_TOKEN = '190040a13eb5b092ca76fa003f58d693c9121e0fc621f6d2ad221468'
    def __init__(self):
        ts.set_token(self.MY_TOKEN)
        self.pro = ts.pro_api()

    def search_stock_daily(self, code):
        pass