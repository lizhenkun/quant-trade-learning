# coding=utf-8
import pandas as pd
import _sys_path_append_
from src.lib.indicator.base_indicator import *


class DataFrameIndicator(object):
    """为数据类型为pandas.DataFrame的数据计算技术指标"""
    @classmethod
    def MA(cls, data_frame, periods=[5, 10, 20], column_name='close', inplace=True):
        """
        Arguments:
            periods: int or list(int)
        """
        column_series = data_frame[column_name]
        if isinstance(periods, int):
            periods = [periods]

        if inplace:
            for N in periods:
                data_frame['MA{}'.format(N)] = MA(column_series, N)
        else:
            return pd.DataFrame({
                'MA{}'.format(N): MA(column_series, N) for N in periods})

    @classmethod
    def EMA(cls, series, n):
        return pd.Series.ewm(series, span=n, min_periods=n-1, adjust=True).mean()

    @classmethod
    def MACD(cls, data_frame, short=12, long=26, mid=9, column_name='close', inplace=True):
        """
        MACD CALC
        """
        column_series = data_frame[column_name]

        dif = cls.EMA(column_series, short) - cls.EMA(column_series, long)
        dea = cls.EMA(dif, mid)
        macd = (dif - dea) * 2

        result = {'DIF': dif, 'DEA': dea, 'MACD': macd}
        new_df = pd.DataFrame(result)

        if inplace:
            data_frame[new_df.keys()] = new_df
        else:
            return new_df

    @classmethod
    def BOLL(cls, data_frame, N=20, P=2, column_name='close', inplace=True):
        column_series = data_frame[column_name]
        boll = MA(column_series, N)
        p_std = P * STD(column_series, N)
        boll_up = boll + p_std
        boll_low = boll - p_std
        result = {'BOLL': boll, 'BOLL_UP': boll_up, 'BOLL_LOW': boll_low}
        new_df = pd.DataFrame(result)
        
        if inplace:
            # 单列添加
            # for key in result:
            #     data_frame[key] = result[key]
            # 增加多列: https://blog.csdn.net/S_o_l_o_n/article/details/102834791
            # 注意这里不能用 result.keys()
            data_frame[new_df.keys()] = new_df
        else:
            return new_df

    @classmethod
    def ENE(cls, data_frame, N=10, M1=11, M2=9, column_name='close', inplace=True):
        column_series = data_frame[column_name]
        _ma = MA(column_series, N)
        ene_up = round((1 + M1 / 100.0) * _ma, 3)
        ene_low = round((1 - M2 / 100.0) * _ma, 3)
        ene = round((ene_up + ene_low) / 2, 3)
        result = {'ENE': ene, 'ENE_UP': ene_up, 'ENE_LOW': ene_low}
        new_df = pd.DataFrame(result)
        if inplace:
            data_frame[new_df.keys()] = new_df
        else:
            return new_df

    @classmethod
    def KDJ(cls, data_frame, N=9, M1=3, M2=3, column_name='close', inplace=True):
        C = data_frame[column_name]
        H = data_frame['high']
        L = data_frame['low']

        RSV = (C - LLV(L, N)) / (HHV(H, N) - LLV(L, N)) * 100
        K = round(SMA(RSV, M1), 3)
        D = round(SMA(K, M2), 3)
        J = round(3 * K - 2 * D, 3)
        result = {'KDJ_K': K, 'KDJ_D': D, 'KDJ_J': J}
        new_df = pd.DataFrame(result)
        if inplace:
            data_frame[new_df.keys()] = new_df
        else:
            return new_df

    @classmethod
    def CCI(cls, data_frame, N=14, column_name='close', inplace=True):
        """
        TYP:=(HIGH+LOW+CLOSE)/3;
        CCI:(TYP-MA(TYP,N))/(0.015*AVEDEV(TYP,N));
        """
        typ = (data_frame['high'] + data_frame['low'] + data_frame[column_name]) / 3
        ## 此处AVEDEV可能为0值  因此导致出错 +0.0000000000001
        cci = ((typ - MA(typ, N)) / (0.015 * AVEDEV(typ, N) + 0.00000001))
        # a = 100
        # b = -100
        # result = {'CCI': cci, 'a': a, 'b': b}
        result = {'CCI': cci}
        new_df = pd.DataFrame(result)
        if inplace:
            data_frame[new_df.keys()] = new_df
        else:
            return new_df

if __name__ == '__main__':
    import os
    import src.lib.constants as ct
    file_name = '000723_day_1997-05-15_2020-03-20.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)

    stock_df1 = pd.read_csv(file_path)
    stock_df2 = DataFrameIndicator.CCI(stock_df1, inplace=True)
    print(stock_df1)
    print(stock_df2)