# coding=utf-8
'''
stock service implements by goldming3 (https://www.myquant.cn/)
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

from gm.api import *

def init(context):
    # 每天14:50 定时执行algo任务
    # schedule(schedule_func=algo, date_rule='daily', time_rule='14:50:00')
    stock_code='SZSE.002713'
    # frequency='1d',
    stock_df = history(
        symbol=stock_code, 
        frequency='5m',
        start_time='2020-02-25',
        end_time='2020-02-28',
        df=True)
    print(stock_df)

    # history_n - 查询历史行情最新n条
    stock_df = history_n(
        symbol=stock_code, 
        frequency='1d',
        count=2000,
        df=True)
    print(stock_df)



if __name__ == '__main__':
    run(strategy_id='6122c38d-5bc6-11ea-a5b2-40234357ebcf',
        filename='goldmining_stock_service.py',
        mode=MODE_BACKTEST,
        token='2dc519d5b2ce0ae92986d8232cb1b69ef4acbc92',
        backtest_start_time='2016-06-17 13:00:00',
        backtest_end_time='2020-02-28 15:00:00')

    