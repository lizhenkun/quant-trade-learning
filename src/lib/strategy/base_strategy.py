# coding=utf-8
import _sys_path_append_

import os
import sys
import abc
import numpy
import pandas as pd
import src.lib.constants as ct
from src.lib.data_helper import resample_data


class BaseStrategy(object):
    REQUIRED_COLUMNS = ['datetime', 'open', 'high', 'low', 'close', 'amount']
    # 收盘时: cash_left: 剩余现金, hold_left: 剩余持仓, avg_cost: 持仓成本, val: 现金+股票市值, profit: 本次盈利
    # op_charge: 操作手续费(手续费+税), highest_close: 买入后遇到的最高收盘价, mov_profit: 移动止盈, mov_lost: 移动止损
    CALULATE_COLUMNS = ['cash_left', 'hold_left', 'avg_cost', 'val', 'profit', 'total_profit']
    def __init__(self, data_or_file, resample_rule=None, rename_cols_dict=None):
        # pandas dataframe object
        self.data_frame = self.load_data(data_or_file, rename_cols_dict)

        if resample_rule:
            self.data_frame = resample_data(self.data_frame, resample_rule)

        df = pd.DataFrame(columns=self.CALULATE_COLUMNS)
        self.data_frame = pd.concat([self.data_frame, df])
        self._prepare_indicator()

    @classmethod
    def load_data(cls, data_or_file, rename_cols_dict=None):
        if isinstance(data_or_file, str):
            data_frame = pd.read_csv(data_or_file)
        else:
            data_frame = data_or_file

        if rename_cols_dict:
            cls._rename_to_required_cols(data_frame, rename_cols_dict)

        columns = set(data_frame.columns.values.tolist())
        assert set(cls.REQUIRED_COLUMNS) <= columns

        # https://blog.csdn.net/the_time_runner/article/details/86619766 需要将str改为时间戳
        # df['datetime'] = pd.to_datetime(df['datetime'])
        data_frame.datetime = pd.to_datetime(data_frame.datetime)
        # 知识点1: reset_index: drop=True: 把原来的索引index列去掉，丢掉
        # 知识点2: inplace=True: 不创建新的对象，直接对原始对象进行修改
        # 知识点2: sort_values、reset_index 都可以添加参数: inplace=True
        # 但加了就需要分三句执行 
        # self.data_frame = self.data_frame[self.REQUIRED_COLUMNS]
        # self.data_frame.sort_values(inplace=True)
        # self.data_frame.reset_index(inplace=True)
        data_frame = data_frame[cls.REQUIRED_COLUMNS].sort_values(
            by=['datetime'], ascending=True).reset_index(drop=True)

        return data_frame

    @classmethod
    def _rename_to_required_cols(cls, data_frame, rename_cols_dict):
        """rename input data columnns name to required columns name"""
        data_frame.rename(columns=rename_cols_dict, inplace=True)

    def load_indicator(self, indicator):
        indicator(self.data_frame, inplace=True)

    def _prepare_indicator(self):
        pass

    def select_times(self, begin, end=None):
        if not end:
            end = self.data_frame.iloc[-1]['datetime']

        self.data_frame = self.data_frame[
            (self.data_frame['datetime'] >= begin) & (self.data_frame['datetime'] <= end)]
        self.data_frame.reset_index(inplace=True, drop=True)

    def _opearate(self, index, row):
        """
        该条K线的操作
        """
        prev_index = index - 1
        prev_row = self.data_frame.loc[prev_index, self.CALULATE_COLUMNS]
        cash_open = prev_row['cash_left']
        hold_open = prev_row['hold_left']
        avg_cost = prev_row['avg_cost']
        total_profit = prev_row['total_profit']

        close = row['close']
        if row['signal_long'] == 1:
            # 买入
            prev_cost = avg_cost * hold_open
            # 可买入数量（100取整)
            hold_add = int(cash_open / (close * 100)) * 100
            hold_left = hold_open + hold_add
            # 此处没有计算手续费
            cost_add = close * hold_add
            
            self.data_frame.at[index, 'hold_left'] = hold_left
            self.data_frame.at[index, 'cash_left'] = cash_open - cost_add
            self.data_frame.at[index, 'avg_cost'] = (prev_cost + cost_add) / hold_left
            self.data_frame.at[index, 'val'] = cash_open + avg_cost * hold_left
            self.data_frame.at[index, 'profit'] = 0
            self.data_frame.at[index, 'total_profit'] = total_profit
        elif row['signal_long'] == 0:
            # 卖出
            # 此处没有计算手续费
            sell_val = hold_open * row['close']
            profit = sell_val - avg_cost * hold_open
            total_profit += profit

            self.data_frame.at[index, 'hold_left'] = 0
            self.data_frame.at[index, 'cash_left'] = cash_open + sell_val
            self.data_frame.at[index, 'avg_cost'] = 0
            self.data_frame.at[index, 'val'] = cash_open + sell_val
            self.data_frame.at[index, 'profit'] = profit
            self.data_frame.at[index, 'total_profit'] = total_profit
        else:
            # 等于上一行的值
            self.data_frame.loc[index,self.CALULATE_COLUMNS] = prev_row
            row = self.data_frame.loc[index]
            self.data_frame.at[index, 'val'] = row['cash_left'] + row['hold_left'] * row['close']
            self.data_frame.at[index, 'profit'] = 0
        # print(iloc, row)

    def backtest(self, init_fund):
        # 同时增加多列
        self.data_frame.loc[
            0, self.CALULATE_COLUMNS] = [0 for index in self.CALULATE_COLUMNS]
        self.data_frame.loc[
            0, ['cash_left', 'val']] = [init_fund, init_fund]
        
        # 首行index是0， 从 index = 1开始遍历
        for index, row in self.data_frame[1:].iterrows():
            self._opearate(index, row)


if __name__ == '__main__':
    file_name = '000723_day_1997-05-15_2020-03-20.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    # rename_cols_dict = {
    #     'datetime': 'candle_time'
    # }
    # base_strategy = BaseStrategy(file_path, rename_cols_dict)
    base_strategy = BaseStrategy(file_path)
    print(type(base_strategy.data_frame['close']))