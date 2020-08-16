#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from datetime import datetime
from datetime import timedelta
import QUANTAXIS as QA
import _sys_path_append_
from src.lib.indicator.dataframe_indicator import DataFrameIndicator
if __package__:
    import src.succ_ratio._public as public
else:
    import _public as public

def get_all_code_list():
    return QA.QA_fetch_stock_list_adv().code.tolist()


def calc_buy_succ_ratio(
    indicator,
    set_buy_sell_signal, 
    observe_periods=public.OBSERVE_PERIODS,
    code_list=public.STOCK_POOL):
    pd.set_option('expand_frame_repr', False)

    now = datetime.now().strftime('%Y-%m-%d')

    data = QA.QA_fetch_stock_day_adv(code_list, '2000-01-01', now)
    qfq_data = data.to_qfq()
    # multiindex 情况下，根据第二个index取出数据
    # qfq_data.data.loc[(slice(None), '300027'), :]
    # qfq_data.data.loc[(slice(None), CODES), :]

    # 遍历所有股票
    output = pd.DataFrame()

    for code in code_list:
        qfq_df = qfq_data.data.loc[(slice(None), code), :]
        qfq_df.reset_index(inplace=True)
        # final_data = qfq_df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']].copy()
        qfq_df = qfq_df[['date', 'code', 'high', 'low', 'close']].copy()

        indicator(qfq_df)
        set_buy_sell_signal(qfq_df)
        qfq_df = qfq_df[['date', 'code', 'high', 'close', 'buy_sell']].copy()

        for period in observe_periods:
            # N天内最高收盘价
            qfq_df['HC%s' % period] = qfq_df['close'].rolling(period).max().shift(-period)
            # N天内最大涨幅
            qfq_df['HCR%s' % period] = (qfq_df['HC%s' % period] / qfq_df['close'] - 1)

        
        # 合并数据
        output = output.append(qfq_df[qfq_df['buy_sell'].notnull()], ignore_index=True)

    print_succ_ratio(output, observe_periods)
    return output


def print_succ_ratio(df, observe_periods):
    # 股票池 整体情况
    for t, group in df.groupby('buy_sell'):
        if t != 'buy':
            continue

        # HCR: 已最高收盘价
        print(group[['HCR%s' % period for period in observe_periods]].describe())
        print('N天内上涨概率\t买入总次数\t买入后上涨次数\t成功率')
        for period in observe_periods:
            label = 'HCR%s' % period
            total = group.shape[0]
            succ = group[group[label] > 0].shape[0]
            ratio = float(succ) / total
            print(f'{period}\t{total}\t{succ}\t{ratio}')
    return


def selector(
    indicator,
    set_buy_sell_signal, 
    code_list=public.STOCK_POOL):
    now = datetime.now()
    before = now - timedelta(days=250)
    period = now - timedelta(days=1)
    
    before = before.strftime('%Y-%m-%d')
    now = now.strftime('%Y-%m-%d')
    period = period.strftime('%Y-%m-%d')
    

    data = QA.QA_fetch_stock_day_adv(code_list, before, now)
    qfq_data = data.to_qfq()
    
    output = pd.DataFrame()

    for code in code_list:
        try:
            qfq_df = qfq_data.data.loc[(slice(None), code), :]
        except:
            continue

        qfq_df.reset_index(inplace=True)
        # final_data = qfq_df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']].copy()
        qfq_df = qfq_df[['date', 'code', 'high', 'low', 'close']].copy()

        indicator(qfq_df)
        set_buy_sell_signal(qfq_df)
        target = qfq_df[(qfq_df.buy_sell == 'buy') & (qfq_df.date >= period)]
        output = output.append(target, ignore_index=True)

        # data = qfq_df.iloc[-1]
        # print(data)
        # if data.buy_sell == 'buy':
        #     print(data.buy_sell, code)
        #     target_stocks.append(code)

    return output