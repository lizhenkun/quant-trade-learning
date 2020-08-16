#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from datetime import datetime
import QUANTAXIS as QA
import _sys_path_append_
from src.lib.indicator.dataframe_indicator import DataFrameIndicator
if __package__:
    from .base import calc_buy_succ_ratio
else:
    from base import calc_buy_succ_ratio


def set_kdj_buy_sell_signal(df):
    buy_position = df['KDJ_K'] > df['KDJ_D']
    buy_2 = df['KDJ_K'] < 20
    df.loc[buy_position[
        (buy_position == True) & (buy_position.shift() == False) & (buy_2 == True)
        ].index, 'buy_sell'] = 'buy'

    sell_position = df['KDJ_K'] < df['KDJ_D']
    df.loc[sell_position[(sell_position == True) 
        & (sell_position.shift() == False)].index, 'buy_sell'] = 'sell'


def main():
    output = calc_buy_succ_ratio(
        DataFrameIndicator.KDJ, set_kdj_buy_sell_signal)
    output.to_csv('kdj.csv', sep='\t', index=False)


if __name__ == '__main__':
    main()
