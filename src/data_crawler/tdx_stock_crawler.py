
# coding=utf-8
'''
pytdx 接口 https://rainx.gitbooks.io/pytdx/content/
Created on 2020-03-01
@author: lizhenkun
@contact: 1292746975@qq.com
'''
if not __package__:
    import _sys_path_append_
else:
    from . import _sys_path_append_

import os
import json
import requests
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame

from pytdx.hq import TdxHq_API
from pytdx.exhq import TdxExHq_API

import src.lib.constants as ct
import src.conf.accounts as accounts



FREQUENT = {
    '5min': 0,
    '15min': 1,
    '30min': 2,
    '60min': 3,
    'day': 4,
    'week': 5,
    'month': 6,
    '1min': 7, # 1分钟
    '1kmin': 8, # 1分钟K线
    'dayk': 9, # 日K线
    'season': 10,
    'year': 11
}


def download_stock_bars(stock_code, freq='day', fq_type='qfq'):
    """获取股票"""
    if stock_code[0] == '0':
        market = 0
    else:
        market = 1
    category = FREQUENT[freq]

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


def download_index_bars(index_code, freq='day', market=None):
    """获取指数
    market -> 市场代码 0:深圳，1:上海
    """
    if not market:
        if stock_code[0] == '3':
            market = 0
        else:
            market = 1
    category = FREQUENT[freq]

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        index = 0
        stock_data = []
        while True:
            older_data = api.get_index_bars(category, market, index_code, index * 800, 800)
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


def _stock_():
    stock_code = '000001'
    freq = 'day'
    # stock_df = download_index_bars(stock_code, freq=freq)
    # print(stock_df)

    csv = os.path.join(ct.DATA_DIR, 'index_%s_%s.csv' % (stock_code, freq))
    stock_df = pd.read_csv(csv)
    html = os.path.join(ct.HTML_DIR, 'index_%s_%s.html' % (stock_code, freq))
    stock_df.to_csv(csv, index=False)
    
    from pyecharts import options as opts
    from pyecharts.charts import Kline

    WIDTH = 1100
    HEIGHT = 550
    chart_init = {
        "width": WIDTH,
        "height": HEIGHT,
    }
    kline = Kline()
    date = stock_df.datetime.tolist()
    data = []
    for index, row in stock_df.iterrows():
        item = [row.open, row.close, row.low, row.high]
        data.append(item)
    print(data)

    kline.add_xaxis(date).add_yaxis('日K', data)
    kline.set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(  
            is_scale=True,  
            splitarea_opts=opts.SplitAreaOpts(  
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)  
            ),
        ),
        datazoom_opts=[opts.DataZoomOpts()],
        # title_opts=opts.TitleOpts(title='日K线图:{0}'.format(ts_code)),
    )
    # kline.add_yaxis(
    #     "日K",
    #     date,
    #     data,
    #     mark_point=["max"],
    #     is_datazoom_show=True,
    # )
    # 生成一个名为 render.html 的文件
    kline.render(html)
    # kline.render('a.html')
    # 在jupyter中使用，只需要使用xxx.render_notebook() 方法即可在Jupyter中显示图
    # kline.render_notebook()


def _exhq_():
    api = TdxExHq_API()
    with api.connect('139.219.103.190', 7721):
        df = api.to_df(api.get_markets())
        print(df)


if __name__ == '__main__':
    _exhq_()