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
    # stock_df = stock_df[['datetime', 'open', 'close']]
    # 分别计算5日、20日、60日的移动平均线
    M1 = 11
    M2 = 9
    N = 10

    stock_df['MA20'] = round(stock_df['close'].rolling(20).mean(), 3)
    stock_df['MA%s' % N] = round(stock_df['close'].rolling(N).mean(), 3)
    stock_df['ENE_UP'] = (1 + M1 / 100.0) * stock_df['MA%s' % N]
    stock_df['ENE_LOW'] = (1 - M2 / 100.0) * stock_df['MA%s' % N]
    stock_df['ENE'] = round((stock_df['ENE_UP'] + stock_df['ENE_LOW'])/2, 3)
    stock_df['ENE_UP'] = round(stock_df['ENE_UP'], 3)
    stock_df['ENE_LOW'] = round(stock_df['ENE_LOW'], 3)

    # ===选取时间段, df = df[df['candle_begin_time'] >= pd.to_datetime('2017-01-01')]
    # stock_df = stock_df[stock_df['datetime'] >= '2014-12-31']
    stock_df = stock_df[stock_df['datetime'] >= '2014-01-01']
    stock_df.reset_index(inplace=True, drop=True)

    # ===找出做多平仓信号: 
    cond1_1 = stock_df['close'].shift(1) >= stock_df['ENE_UP'].shift(1)  # 昨天超过顶部
    cond1_2 = stock_df['low'] <= stock_df['ENE_UP']  # 今天触碰顶部

    cond2_1 = stock_df['close'].shift(1) > stock_df['MA20'].shift(1)
    cond2_2 = stock_df['close'] < stock_df['MA20']

    cond3_1 = stock_df['close'].shift(1) < stock_df['ENE_LOW'].shift(1) # 昨天在底部
    cond3_2 = stock_df['close'] < stock_df['ENE_LOW'] # 今天也在底部

    sell_cond = (cond1_1 & cond1_2) | (cond2_1 & cond2_2) | (cond3_1 & cond3_2)
    # sell_cond = (cond1_1 & cond1_2) | (cond3_1 & cond3_2)
    # 将产生平仓信号当天的signal设置为0，0代表平仓
    stock_df.loc[sell_cond, 'signal_long'] = 0

    # ===找出做多信号
    cond1_1 = stock_df['close'].shift(1) > stock_df['ENE_LOW'].shift(1)  # 昨天没到达底部
    cond1_2 = stock_df['low'] < stock_df['ENE_LOW'] # 今天到达底部

    cond2_1 = stock_df['close'].shift(1) < stock_df['ENE_LOW'].shift(1)  # 昨天到达底部
    cond2_2 = stock_df['close'] >= stock_df['ENE_LOW'] # 今天上穿底部

    cond3_1 = stock_df['close'].shift(1) < stock_df['MA20'].shift(1)  # 昨天<MA20
    cond3_2 = stock_df['close'] > stock_df['MA20']  # 今天 > MA20

    cond4_1 = stock_df['close'].shift(1) > stock_df['MA20'].shift(1)  # 昨天>MA20
    cond4_2 = stock_df['low'] < stock_df['MA20']  # 今天lowest > MA20
    cond4_3 = stock_df['close'] > stock_df['MA20']  # 今天close > MA20

    buy_cond = (cond1_1 & cond1_2) | (cond2_1 & cond2_2) | (
        cond3_1 & cond3_2) | (cond4_1 & cond4_2 & cond4_3)
    stock_df.loc[buy_cond, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

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
            # print(index, row)
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


    # # ===删除不必要的数据
    stock_df.drop(['amount', 'MA10', 'signal_long', 'keep', 'cash_open'], axis=1, inplace=True)
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)
    print(stock_df)
    # stock_df.to_csv('ene.csv')

if __name__ == '__main__':
    # file_name = '000723_day_1997-05-15 15:00_2020-03-06 15:00.csv'
    # file_name = '000723.SZ_qfq.csv'
    file_name = '000723_day_1997-05-15_2020-03-06.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    run(file_path)