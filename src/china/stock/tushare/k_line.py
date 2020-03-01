# -*- coding: UTF-8 -*-
import os
import pandas as pd
import tushare as ts
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Kline


def abc():
    ts_code='002713.SZ'
    csv_file = '{0}.csv'.format(ts_code)
    render_html = '{0}.html'.format(ts_code)
    end_date = datetime.now().strftime('%Y%m%d')

    df = None
    if not os.path.exists(csv_file):
        MY_TOKEN = '190040a13eb5b092ca76fa003f58d693c9121e0fc621f6d2ad221468'
        ts.set_token(MY_TOKEN)
        pro = ts.pro_api()
        df1 = pro.daily(ts_code=ts_code, start_date='20140101', end_date=end_date)
        df = df1.sort_values(by=['trade_date'])
        df.reset_index(level=0, inplace=True)
        df.drop(['index'], axis=1, inplace=True)
        print(df)
        df.to_csv(csv_file)

    if not df is None:
        df = pd.read_csv(csv_file)

    date = df.trade_date.tolist()
    data = []
    for idx in df.index :
        row=[df.iloc[idx]['open'],df.iloc[idx]['close'],df.iloc[idx]['low'],df.iloc[idx]['high']]
        data.append(row)
    WIDTH = 1100
    HEIGHT = 550
    chart_init = {
        "width": WIDTH,
        "height": HEIGHT,
    }
    kline = Kline()
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

    kline.render(render_html)
    kline.render_notebook()
    # kline.render('a.html')
    # 在jupyter中使用，只需要使用xxx.render_notebook() 方法即可在Jupyter中显示图