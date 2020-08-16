# coding=utf-8
if __package__:
    from . import _sys_path_append_
else:
    import _sys_path_append_

import os
import sys
import numpy
import pandas as pd

import src.lib.constants as ct
from src.lib.strategy.base_strategy import BaseStrategy
from src.lib.indicator.base_indicator import *
from src.lib.indicator.dataframe_indicator import DataFrameIndicator


class KDStrategy(BaseStrategy):
    def __init__(self, data_or_file, resample_rule=None, rename_cols_dict=None):
        super(KDStrategy, self).__init__(data_or_file, resample_rule, rename_cols_dict)

    def _prepare_indicator(self):
        self.load_indicator(DataFrameIndicator.KDJ)

    def buy_condition(self):
        # K 金叉 D
        cond1 = CROSS(self.data_frame['KDJ_K'], self.data_frame['KDJ_D'])
        # 超卖，严格要求是20
        cond2 = self.data_frame['KDJ_K'] < 25
        return cond1 & cond2

    def close_buy_condition(self):
        return CROSS(self.data_frame['KDJ_D'], self.data_frame['KDJ_K']) & True

    def sell_condition(self):
        # K 死叉 D
        cond1 = CROSS(self.data_frame['KDJ_D'], self.data_frame['KDJ_K'])
        # 慢线超买，严格要求是80
        cond2 = self.data_frame['KDJ_K'] > 75
        return cond1 & cond2
    
    def close_sell_condition(self):
        return CROSS(self.data_frame['KDJ_K'], self.data_frame['KDJ_D']) & True

    def add_signal(self):
        self.data_frame.loc[self.buy_condition(), 'signal_long'] = 1
        self.data_frame.loc[self.close_buy_condition(), 'signal_long'] = 0

        self.data_frame.loc[self.sell_condition(), 'signal_short'] = -1
        self.data_frame.loc[self.close_sell_condition(), 'signal_short'] = 0

if __name__ == '__main__':
    # file_name = '000723_day_1997-05-15_2020-03-27.csv'
    file_name = '600864_day_1994-08-09_2020-03-27.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    # strategy = KDStrategy(file_path)
    # strategy = KDStrategy(file_path, resample_rule='1W')
    strategy = KDStrategy(file_path, resample_rule='M')
    strategy.add_signal()
    strategy.select_times('1999-01-01')
    strategy.backtest(init_fund=30000)

    # strategy.data_frame.to_csv('kd.csv')
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)
    print(strategy.data_frame)
