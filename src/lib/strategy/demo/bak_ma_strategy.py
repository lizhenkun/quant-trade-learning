# coding=utf-8
if not __package__:
    import _sys_path_append_

import os
import numpy
import pandas as pd
import src.lib.constants as ct


def run(file_path):
    # 
    stock_df = pd.read_csv(file_path)
    stock_df = stock_df[['datetime', 'open', 'close']]
    # 分别计算5日、20日、60日的移动平均线
    ma_list = [3, 5, 20]

    for ma in ma_list:
        stock_df['MA{0}'.format(ma)] = round(stock_df['close'].rolling(ma).mean(), 3)

    # ===找出做多信号: 股价上穿MA20
    condition1 = stock_df['close'] > stock_df['MA20']  # 当前K线的收盘价 > MA20
    condition2 = stock_df['close'].shift(1) <= stock_df['MA20'].shift(1)  # 之前K线的收盘价 <= MA20
    buy_cond = condition1 & condition2
    stock_df.loc[buy_cond, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # ===找出做多平仓信号: MA3 下穿 MA5 或 连续两天收盘价在MA3下方
    condition1 = stock_df['MA3'] < stock_df['MA5']
    condition2 = stock_df['MA3'].shift(1) >= stock_df['MA5'].shift(1)
    condition3 = stock_df['close'] < stock_df['MA3']
    condition4 = stock_df['close'].shift(1) < stock_df['MA3'].shift(1)
    sell_cond = (condition1 & condition2) | (condition3 & condition4)
    # 将产生平仓信号当天的signal设置为0，0代表平仓
    stock_df.loc[sell_cond, 'signal_long'] = 0

    # 去除重复信号: 连续出现相同信号的
    # 1. 选出信号非空的行
    temp = stock_df[stock_df['signal_long'].notnull()][['signal_long']]
    # 2. 选出前后信号不同的行
    temp = temp[temp['signal_long'] != temp['signal_long'].shift(1)]
    # 3. 赋值(感觉dataframe会按照 index 相同的 赋值，不相同的会设为Null)
    stock_df['signal_long'] = temp['signal_long']

    # 第二根K线才操作
    stock_df['op'] = stock_df['signal_long'].shift()

    stock_df['keep'] = stock_df['op']
    stock_df['keep'].fillna(method='ffill', inplace=True)
    # 将初始行数的position补全为0
    stock_df['keep'].fillna(value=0, inplace=True)

    # ===选取时间段, df = df[df['candle_begin_time'] >= pd.to_datetime('2017-01-01')]
    # stock_df = stock_df[stock_df['datetime'] >= '2014-12-31']
    stock_df = stock_df[stock_df['datetime'] >= '2014-01-01']
    stock_df.reset_index(inplace=True, drop=True)

    # 同时增加多列
    columns = ['cash_open', 'hold', 'cash_left', 'val']
    df = pd.DataFrame(columns=columns)
    stock_df = pd.concat([stock_df, df])

    start_money = 10000
    columns = ['cash_open', 'hold', 'cash_left', 'val']
    stock_df.at[0, columns] = [
        start_money, 0, start_money, start_money]


    for index, row in stock_df.iterrows():
        if pd.isnull(row.op): # 没有新操作
            if row.keep == 0 and index != 0: # 不持仓
                # print(row[columns])
                # print(stock_df.loc[index - 1, columns])
                # 直接赋值给row， 循环退出后不会改变dataframe
                # row['cash_open', 'hold', 'cash_left', 'val'] = stock_df.loc[index - 1, columns]
                # 给指定行的某几列赋值 df.loc[rowIndex, [col1, col2]] = []
                # stock_df.loc[index, columns] = stock_df.loc[index - 1, columns]
                stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
                stock_df.loc[index, 'hold'] = stock_df.loc[index - 1, 'hold']
                stock_df.loc[index, 'cash_left'] = stock_df.loc[index, 'cash_open']
                stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left']
            elif row.keep == 1:
                stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
                stock_df.loc[index, 'hold'] = stock_df.loc[index - 1, 'hold']
                stock_df.loc[index, 'cash_left'] = stock_df.loc[index - 1, 'cash_left']
                stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left'] + stock_df.loc[index, 'hold'] * stock_df.loc[index, 'close']
        elif row.op == 1: # 开盘买入
            cash_open = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'cash_open'] = cash_open
            stock_df.loc[index, 'hold'] = int(cash_open / stock_df.loc[index, 'open'] / 100) * 100
            stock_df.loc[index, 'cash_left'] = cash_open - stock_df.loc[index, 'hold'] * stock_df.loc[index, 'open']
            stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left'] + stock_df.loc[index, 'hold'] * stock_df.loc[index, 'close']
            # break
        elif row.op == 0: # 开盘卖出
            hold = stock_df.loc[index - 1, 'hold']
            stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'hold'] = 0
            stock_df.loc[index, 'cash_left'] = stock_df.loc[index, 'cash_open'] + hold * stock_df.loc[index, 'open']
            stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left']


    # ===删除不必要的数据
    stock_df.drop(['MA3', 'MA5', 'MA20', 'signal_long', 'keep'], axis=1, inplace=True)
    pd.set_option('display.max_rows', None)
    # print(stock_df[500:])
    # print(stock_df[:20])
    print(stock_df)

if __name__ == '__main__':
    # file_name = '000723_day_1997-05-15 15:00_2020-03-06 15:00.csv'
    # file_name = '000723.SZ_qfq.csv'
    file_name = '000723_day_1997-05-15_2020-03-06.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    run(file_path)