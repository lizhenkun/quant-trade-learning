# coding=utf-8
import _sys_path_append_

import os
import sys
import numpy
import pandas as pd
import src.lib.constants as ct
from src.strategy.base_strategy import BaseStrategy
from src.lib.indicator.dataframe_indicator import DataFrameIndicator


class EneStrategy(BaseStrategy):
    def __init__(self, data_or_file, rename_cols_dict=None):
        super(EneStrategy, self).__init__(data_or_file, rename_cols_dict)

        self.load_indicator(DataFrameIndicator.ENE)


    def _prepare_indicator(self):
        self.load_indicator(DataFrameIndicator.ENE)

def run(file_path):
    # 
    stock_df = pd.read_csv(file_path)
    # stock_df = stock_df[['datetime', 'open', 'close']]
    # 分别计算5日、20日、60日的移动平均线
    M1 = 11
    M2 = 9
    N = 10

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

    # # ===找出做多平仓信号:
    # # 连续破下跪
    # cond1_1 = stock_df['ENE_LOW'].shift(1) < stock_df['ENE_LOW']
    # cond1_2 = stock_df['close'].shift(1) < stock_df['ENE_LOW'].shift(1)
    # cond1_3 = stock_df['close'] < stock_df['close'].shift(1)
    
    # # 连续破中轨
    # cond2_1 = stock_df['ENE'].shift(1) < stock_df['ENE']
    # cond2_2 = stock_df['close'].shift(1) < stock_df['ENE'].shift(1)
    # cond2_3 = stock_df['close'] < stock_df['close'].shift(1)

    # 下穿上轨
    cond3_1 = stock_df['close'].shift(1) >= stock_df['ENE_UP'].shift(1)
    cond3_2 = stock_df['close'] < stock_df['ENE_UP']

    # sell_cond = (cond1_1 & cond1_2 & cond1_3) | (cond2_1 & cond2_2 & cond2_3) & (cond3_1 & cond3_2)
    sell_cond = (cond3_1 & cond3_2)
    stock_df.loc[sell_cond, 'signal'] = 0
    # 第二根K线才操作 -- 跌停开盘不操作
    stock_df.loc[sell_cond, 'reason'] = '下穿上轨'
    
    # ===找出做多信号
    # cond1: 到达底部 & 不能是中阴线
    cond1_1 = stock_df['low'].shift(1) > stock_df['ENE_LOW'].shift(1)
    cond1_2 = stock_df['low'] < stock_df['ENE_LOW']
    cond1_3 = stock_df['close'] / stock_df['close'].shift(1) > 0.95

    # cond2: 上穿底部
    cond2_1 = stock_df['close'].shift(1) < stock_df['ENE_LOW'].shift(1)
    cond2_2 = stock_df['close'] >= stock_df['ENE_LOW'] # 今天上穿底部

    # cond3: 上传中轨
    cond3_1 = stock_df['close'].shift(1) < stock_df['ENE'].shift(1)
    cond3_2 = stock_df['close'] >= stock_df['ENE']

    buy_cond = (cond1_1 & cond1_2 & cond1_3) | (cond2_1 & cond2_2) | (cond3_1 & cond3_2)
    # 第二根K线才操作 -- 跌停开盘不操作
    stock_df.loc[buy_cond, 'signal'] = 1
    # 第二根K线才操作 -- 跌停开盘不操作
    stock_df['op'] = stock_df['signal'].shift()
    # 开盘跌停 或 涨停不买入
    cond_op = stock_df['op'] == 1
    cond_dt = stock_df['open'] / stock_df['close'].shift(1) < 0.98
    cond_zt = stock_df['open'] / stock_df['close'].shift(1) > 1.08

    stock_df.loc[cond_op & (cond_dt | cond_zt), 'op'] = None
    # 记录开仓时的价格
    stock_df.loc[stock_df['op'] == 1, 'open_price'] = stock_df['open']
    stock_df['open_price'].fillna(method='ffill', inplace=True)
    stock_df['keep'] = stock_df['op']
    stock_df['keep'].fillna(method='ffill', inplace=True)
    # 将初始行数的 keep 补全为0
    stock_df['keep'].fillna(value=0, inplace=True)
    
    # 同时增加多列
    columns = ['cash_open', 'hold', 'avg_price', 'highest_close', 'cash_left', 'val', 'lost', 'zhiying']
    df = pd.DataFrame(columns=columns)
    stock_df = pd.concat([stock_df, df])

    start_money = 30000
    buy_times = 3
    left_buy_times = 3

    stock_df.at[0, columns] = [
        start_money, 0, 0.0, 0.0, start_money, start_money, 0, 0]
    temp = stock_df[columns].fillna(method='ffill')
    stock_df[columns] = temp[columns]
    
    for index, row in stock_df.iterrows():
        op = stock_df.loc[index, 'op']
        keep = stock_df.loc[index, 'keep']
        if op == 1: # 开盘买入, 分批买入
            cash_open = stock_df.loc[index - 1, 'cash_left']
            # 上次持仓
            hold = stock_df.loc[index - 1, 'hold']
            # 上次成本
            cost = stock_df.loc[index - 1, 'avg_price'] * hold
            avg_price = stock_df.loc[index - 1, 'avg_price']
            cash_left = cash_open
            if left_buy_times >= 1:
                buy = cash_open / left_buy_times
                left_buy_times -= 1
                
                cur_hold = int(buy / row.open / 100) * 100
                # 本次成本
                cur_cost = cur_hold * row.open
                hold += cur_hold
                avg_price = (cost + cur_cost) / hold
                cash_left = cash_open - cur_cost

                stock_df.loc[index, 'highest_close'] = row.close
            else:
                stock_df.loc[index, 'highest_close'] = stock_df.loc[index - 1, 'highest_close']

            stock_df.loc[index, 'cash_open'] = cash_open
            stock_df.loc[index, 'hold'] = hold
            stock_df.loc[index, 'avg_price'] = avg_price
            stock_df.loc[index, 'cash_left'] = cash_left
            stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left'] + stock_df.loc[index, 'hold'] * stock_df.loc[index, 'close']
            
            stock_df.loc[index + 1, 'keep'] = 1
        elif op == 0 and left_buy_times < buy_times:
            cash_left = stock_df.loc[index - 1, 'cash_left']
            sell_price = row.close * stock_df.loc[index - 1, 'hold']
            stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'avg_price'] = 0
            stock_df.loc[index, 'hold'] = 0
            stock_df.loc[index, 'cash_left'] = cash_left + sell_price
            stock_df.loc[index, 'val'] = cash_left + sell_price
            stock_df.loc[index, 'highest_close'] = 0
            left_buy_times = buy_times
            stock_df.loc[index + 1, 'keep'] = 0
        elif keep == 1: # 持有
            stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'avg_price'] = stock_df.loc[index - 1, 'avg_price']
            stock_df.loc[index, 'hold'] = stock_df.loc[index - 1, 'hold']
            stock_df.loc[index, 'cash_left'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'val'] = stock_df.loc[index, 'cash_left'] + stock_df.loc[index, 'hold'] * stock_df.loc[index, 'close']
            stock_df.loc[index, 'highest_close'] = row.close if row.close > stock_df.loc[index - 1, 'highest_close'] else stock_df.loc[index - 1, 'highest_close']
            stock_df.loc[index + 1, 'keep'] = 1
            
            # 判断是否要止损
            lost = row.close / stock_df.loc[index, 'avg_price']
            stock_df.loc[index, 'lost'] = lost

            highest_close = stock_df.loc[index, 'highest_close']
            zhiying = row.close / highest_close
            stock_df.loc[index, 'zhiying'] = zhiying

            # 损失 10%
            if lost < 0.9:
                # 第二天卖出
                stock_df.loc[index + 1, 'op'] = 0
                stock_df.loc[index + 1, 'keep'] = 0
                stock_df.loc[index + 1, 'reason'] = '止损'
            elif lost > 1:
                # 移动止盈 5%
                if zhiying < 0.95:
                    # 第二天卖出
                    stock_df.loc[index + 1, 'op'] = 0
                    stock_df.loc[index + 1, 'keep'] = 0
                    stock_df.loc[index + 1, 'reason'] = '止盈'
        elif index != 0: # and row.keep == 0
            stock_df.loc[index, 'cash_open'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'avg_price'] = stock_df.loc[index - 1, 'avg_price']
            stock_df.loc[index, 'hold'] = stock_df.loc[index - 1, 'hold']
            stock_df.loc[index, 'cash_left'] = stock_df.loc[index - 1, 'cash_left']
            stock_df.loc[index, 'val'] = stock_df.loc[index - 1, 'val']
            stock_df.loc[index, 'highest_close'] = 0
            stock_df.loc[index + 1, 'keep'] = 0

    # # ===删除不必要的数据
    # stock_df.drop(['amount', 'MA10', 'MA20', 'ENE_LOW', 'ENE', 'open_price'], axis=1, inplace=True)
    headers = ['datetime', 'open', 'high', 'close', 'op', 'keep', 'cash_open',
        'hold', 'avg_price', 'highest_close', 'val', 'lost', 'zhiying', 'reason']
    stock_df = stock_df[headers]
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)
    stock_df.to_csv('ene.csv')

if __name__ == '__main__':
    # file_name = '000723_day_1997-05-15 15:00_2020-03-06 15:00.csv'
    # file_name = '000723.SZ_qfq.csv'
    file_name = '000723_day_1997-05-15_2020-03-20.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    run(file_path)