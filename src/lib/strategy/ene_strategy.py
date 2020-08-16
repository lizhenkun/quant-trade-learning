# coding=utf-8
import _sys_path_append_

import os
import sys
import numpy
import pandas as pd
import src.lib.constants as ct
from src.lib.strategy.base_strategy import BaseStrategy
from src.lib.indicator.dataframe_indicator import DataFrameIndicator


class ENEStrategy(BaseStrategy):
    def __init__(self, data_or_file, rename_cols_dict=None):
        super(ENEStrategy, self).__init__(data_or_file, rename_cols_dict)

    def _prepare_indicator(self):
        self.load_indicator(DataFrameIndicator.ENE)


if __name__ == '__main__':
    file_name = '000723_day_1997-05-15_2020-03-20.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    # rename_cols_dict = {
    #     'datetime': 'candle_time'
    # }
    # base_strategy = BaseStrategy(file_path, rename_cols_dict)
    strategy = ENEStrategy(file_path)