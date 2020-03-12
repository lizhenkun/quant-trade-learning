# coding=utf-8
import os
import pandas as pd
import lib.constants as ct


def save_data(stock_df, stock_code, frequent, file_type='csv'):
    begin_time = stock_df.iloc[0]['datetime']
    end_time = stock_df.iloc[-1]['datetime']
    file_name = '{stock}_{freq}_{begin}_{end}.{file_type}'.format(
        stock=stock_code, freq=frequent,
        begin=begin_time, end=end_time, file_type=file_type)
    
    file_path = os.path.join(ct.CHINA_STOCK_DATA_DIR, file_name)
    if file_type == 'csv':
        stock_df.to_csv(file_path, index=False)
    else:
        stock_df.to_hdf(file_path, key='all_data', mode='w', index=False)
    return file_path


def resample_data(file, rule_type):
    file_type = file.rsplit('.', 1)[-1]
    if file_type == 'csv':
        stock_df = pd.read_csv(file)
    else:
        stock_df = pd.read_hdf(file)
    
    # https://blog.csdn.net/the_time_runner/article/details/86619766 需要将str改为时间戳
    # df['datetime'] = pd.to_datetime(df['datetime'])
    stock_df.datetime = pd.to_datetime(stock_df.datetime)
    stock_df.set_index('datetime', drop=True)
    # https://www.cnblogs.com/jingsupo/p/pandas-resample.html
    # 使用datetime列重新采样,
    # closed = ‘right’ 在降采样时, 各时间段的哪一段是闭合的, ‘right’或‘left’, 默认‘right’
    # label = ‘right’  在降采样时, 如何设置聚合值的标签，例如，9:30-9:35会被标记成9:30还是9:35,默认9:35(right)
    stock_df = stock_df.resample(rule=rule_type, on='datetime', closed='right', label='right')
    # agg: 按列聚合 https://segmentfault.com/a/1190000012394176?utm_source=tag-newest
    stock_df = stock_df.agg({
        'open': 'first', # 使用第一列
        'high': 'max', # 使用最大值
        'low': 'min', # 使用最小值
        'close': 'last', # 使用最后一列
        'vol': 'sum', # 求和
        'amount': 'sum', # 求和
    })
    return stock_df


if __name__ == '__main__':
    pass