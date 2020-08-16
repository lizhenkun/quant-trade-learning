# coding=utf-8
"""
基本技术指标
"""
import pandas as pd
import numpy as np

def CROSS(A, B):
    """
    A金叉B, A<B then A>B
    Arguments:
        A {[type]} -- [description]
        B {[type]} -- [description]
    Returns:
        [type] -- [description]
    """
    var = np.where(A < B, 1, 0)
    try:
        index = A.index
    except:
        index = B.index
    # diff: https://blog.csdn.net/A1518643337/article/details/78289165
    # apply: https://blog.csdn.net/stone0823/article/details/100008619, apply(int): 效果: int(结果): 将结果转为整数
    return (pd.Series(var, index=index).diff() < 0).apply(int)

def MA(Series, N):
    """移动平均线"""
    return pd.Series.rolling(Series, N).mean()

def EMA(Series, N):
    return pd.Series.ewm(Series, span=N, min_periods=N - 1, adjust=True).mean()

def SMA(Series, N, M=1):
    """
    威廉SMA算法: 参考https://www.joinquant.com/post/867
    本次修正主要是对于返回值的优化,现在的返回值会带上原先输入的索引index
    2018/5/3
    @yutiansut
    """
    ret = []
    i = 1
    length = len(Series)
    # 跳过X中前面几个 nan 值
    while i < length:
        if np.isnan(Series.iloc[i]):
            i += 1
        else:
            break
    preY = Series.iloc[i]
    ret.append(preY)
    while i < length:
        Y = (M * Series.iloc[i] + (N - M) * preY) / float(N)
        ret.append(Y)
        preY = Y
        i += 1
    return pd.Series(ret, index=Series.tail(len(ret)).index)

def STD(Series, N):
    """方差
    https://blog.csdn.net/u011587322/article/details/80934096
    """
    return pd.Series.rolling(Series, N).std()

def AVEDEV(Series, N):
    """
    平均绝对偏差 mean absolute deviation
    修正: 2018-05-25 
    之前用mad的计算模式依然返回的是单值
    """
    return Series.rolling(N).apply(lambda x: (np.abs(x - x.mean())).mean(), raw=True)

def LLV(Series, N):
    """最近一段时间最小值"""
    return pd.Series(Series).rolling(N).min()

def HHV(Series, N):
    """最近一段时间最大值"""
    return pd.Series(Series).rolling(N).max()


if __name__ == '__main__':
    import os
    import _sys_path_append_
    import src.lib.constants as ct
    
    file_name = '000723_day_1997-05-15_2020-03-20.csv'
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)

    stock_df = pd.read_csv(file_path)
    series = BaseIndicator.MA(stock_df['close'], 5)
    print(series)