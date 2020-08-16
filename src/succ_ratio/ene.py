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


def set_ene_buy_sell_signal(df):
    buy_position = df['ENE_LOW'] > df['low']
    df.loc[buy_position[buy_position == True].index, 'buy_sell'] = 'buy'
    sell_position = df['ENE_UP'] < df['high']
    df.loc[sell_position[(sell_position == True) 
        & (sell_position.shift() == False)].index, 'buy_sell'] = 'sell'


def main():
    output = calc_buy_succ_ratio(
        DataFrameIndicator.ENE, set_ene_buy_sell_signal)
    output.to_csv('ene.csv', sep='\t', index=False)


if __name__ == '__main__':
    main()
