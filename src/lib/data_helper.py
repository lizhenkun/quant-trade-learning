# coding=utf-8
import os
import pandas as pd
import src.lib.constants as ct


def load_exists_data(stock_code, frequent, fq_type, file_type='csv'):
    """加载本地已有数据"""
    file_name = '{stock}_{freq}_{fq_type}.{file_type}'.format(
        stock=stock_code, freq=frequent, fq_type=fq_type, file_type=file_type)
    
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    data_frame = None
    if os.path.exists(file_path):
        if file_type == 'csv':
            data_frame = pd.read_csv(file_path)
        else:
            data_frame = pd.read_hdf(file_path)
    return data_frame


def save_data(stock_df, stock_code, frequent, fq_type, file_type='csv'):
    begin_time = stock_df.iloc[0]['datetime']
    end_time = stock_df.iloc[-1]['datetime']
    file_name = '{stock}_{freq}.{file_type}'.format(
        stock=stock_code, freq=frequent,
        begin=begin_time, end=end_time, file_type=file_type)
    
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    if file_type == 'csv':
        stock_df.to_csv(file_path, index=False)
    else:
        stock_df.to_hdf(file_path, key='all_data', mode='w', index=False)
    return file_path


def resample_data(stock_df, resample_rule, on_col='datetime'):
    """
    resample_rule: https://blog.csdn.net/brucewong0516/article/details/84768464
    T: minute, 15T 15minute
    H: hour
    W: week
    M: month
    """
    # stock_df.set_index(on_col, drop=True)
    # https://www.cnblogs.com/jingsupo/p/pandas-resample.html
    # 使用datetime列重新采样,
    # closed = ‘right’ 在降采样时, 各时间段的哪一段是闭合的, ‘right’或‘left’, 默认‘right’
    # label = ‘right’  在降采样时, 如何设置聚合值的标签，例如，9:30-9:35会被标记成9:30还是9:35,默认9:35(right)
    stock_df = stock_df.resample(rule=resample_rule, on=on_col, closed='right', label='right')
    # agg: 按列聚合 https://segmentfault.com/a/1190000012394176?utm_source=tag-newest
    stock_df = stock_df.agg({
        'open': 'first', # 使用第一列
        'high': 'max', # 使用最大值
        'low': 'min', # 使用最小值
        'close': 'last', # 使用最后一列
        'amount': 'sum', # 求和
    })
    stock_df = stock_df[stock_df['open'].notnull()]
    # 重置inddex， 否则 datetime作为index，相当于少了datetime一列
    stock_df.reset_index(inplace=True)
    return stock_df


if __name__ == '__main__':
    pass