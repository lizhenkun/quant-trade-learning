# from pyecharts.charts.basic_charts.kline import Kline
import os
import tushare as ts
import pandas as pd
from datetime import datetime

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
# pd.set_option('precision', 3)
# None - 全打印
pd.set_option('display.max_rows', 300)
# 总行数超过300时，设为300没有用
# pd.set_option('display.max_rows', 300)

ts_code='002713.SZ'
csv_file = 'reorg_{0}.csv'.format(ts_code)
stock_df = pd.read_csv(csv_file)
# print(df)

# 分别计算5日、20日、60日的移动平均线
ma_list = [3, 5, 20]

for ma in ma_list:
    stock_df['MA{0}'.format(ma)] = round(stock_df['close'].rolling(ma).mean(), 3)

# ===找出做多信号: 股价上穿MA20
condition1 = stock_df['close'] > stock_df['MA20']  # 当前K线的收盘价 > MA20
condition2 = stock_df['close'].shift(1) <= stock_df['MA20'].shift(1)  # 之前K线的收盘价 <= MA20
buy_cond = condition1 & condition2
stock_df.loc[buy_cond, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多
# print(stock_df)

# ===找出做多平仓信号: MA3 下穿 MA5 或 连续两天收盘价在MA3下方
condition1 = stock_df['MA3'] < stock_df['MA5']
condition2 = stock_df['MA3'].shift(1) >= stock_df['MA5'].shift(1)
condition3 = stock_df['close'] < stock_df['MA3']
condition4 = stock_df['close'].shift(1) < stock_df['MA3'].shift(1)
sell_cond = (condition1 & condition2) | (condition3 & condition4)
stock_df.loc[sell_cond, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

# 去除重复信号
temp = stock_df[stock_df['signal_long'].notnull()][['signal_long']]
print(temp)
temp = temp[temp['signal_long'] != temp['signal_long'].shift(1)]
print(temp)
stock_df['signal_long'] = temp['signal_long']
print(stock_df)

# ===选取时间段
stock_df = stock_df[stock_df['trade_date'] >= 20150101]
stock_df.reset_index(inplace=True, drop=True)
print(stock_df)
# 只保留有信号的行 - 看不到每日变化，不适合有爆仓的情况, 
# signal_df = stock_df[stock_df['signal_long'].notnull()]
#signal_df = signal_df[signal_df['signal_long'] != signal_df['signal_long'].shift(1)]
#print(signal_df)

init_cash = 10000
# stock_df[] = 0

# 只保留第一次出现信号的行

