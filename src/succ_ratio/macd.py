#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from datetime import datetime
import QUANTAXIS as QA
import _sys_path_append_
from src.lib.indicator.dataframe_indicator import DataFrameIndicator
if __package__:
    from ._public import *
    from .base import *
else:
    from base import *
    from _public import *


def set_macd_bl_buy_sell_signal(df):
    """macd 背离: 股价新高，DIF/红柱非新高"""
    N = 60
    # 股价创新低， dif没创新低
    cond_k_min = df['close'] == df['close'].rolling(N).min()
    cond_diff_min = df['DIF'] > df['DIF'].rolling(N).min()
    df.loc[cond_k_min[(cond_k_min == True) 
        & (cond_diff_min == True)].index, 'buy_sell'] = 'buy'

    # # 股价创新高， dif没创新高
    # cond_k_max = df['close'] == df['close'].rolling(N).max()
    # cond_diff_max = df['DIF'] < df['DIF'].rolling(N).max()
    # df.loc[cond_k_max[(cond_k_max == True) 
    #     & (cond_diff_max == True)].index, 'buy_sell'] = 'sell'


def succ_ratio():
    output = calc_buy_succ_ratio(
        DataFrameIndicator.MACD, set_macd_bl_buy_sell_signal)
    output.to_csv('macd.csv', sep='\t', index=False)


def select_stocks():
    # code_list = get_all_code_list()
    code_list = ALL_STOCKS
    output = selector(
        indicator=DataFrameIndicator.MACD
        , set_buy_sell_signal=set_macd_bl_buy_sell_signal
        , code_list=code_list
    )
    now = datetime.now().strftime('%Y-%m-%d')
    output.to_csv('macd_selector_%s.csv' % now, sep='\t', index=False)
    print(output)

if __name__ == '__main__':
    succ_ratio()
    # select_stocks()