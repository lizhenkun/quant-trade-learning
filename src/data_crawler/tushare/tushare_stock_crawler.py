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
import tushare as ts
from datetime import datetime

import _sys_path_append_
import src.lib.constants as ct
import src.conf.accounts as accounts


def request_stock_daily(ts_code: str, start_date: str = None, 
    end_date: str = None) -> pd.DataFrame:
    """
    @see https://www.waditu.com/document/2?doc_id=27
    Arguments:
        ts_code: 股票代码（支持多个股票同时提取，逗号分隔）, eg. '000001.SZ,600000.SH'
        start_date: 开始日期(YYYYMMDD), None 则从该股第一天开始
        end_date: 结束日期(YYYYMMDD), None则截止至最近收盘日
    Returns:
        pandas.DataFrame
    """
    if end_date:
        end_date = datetime.now().strftime('%Y%m%d')

    ts.set_token(accounts.TUSHARE_TOKEN)
    pro = ts.pro_api()
    # 获取前复权数据
    df = pro.daily(ts_code=ts_code, adj='qfq',
      start_date=start_date, end_date=end_date)
    return df


if __name__ == '__main__':
    stock_code='000723.SZ'
    start_date = '19970515'
    end_date = datetime.now().strftime('%Y%m%d')
    df = request_stock_daily(stock_code, start_date, end_date)
    df['datetime'] = pd.to_datetime(df['trade_date'])
    df = df[['datetime', 'open', 'high', 'low', 'close', 'vol', 'amount']]\
        .sort_values('datetime').reset_index(drop=True)
    # df
    csv_file = os.path.join(ct.CHINA_STOCK_DATA_DIR, '{0}_qfq.csv'.format(stock_code))
    df.to_csv(csv_file, index=False)
    print('save to file: %s' % csv_file)
    print(df)
