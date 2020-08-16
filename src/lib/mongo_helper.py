# coding=utf-8
import os
import pymongo
import pandas as pd

# 打开docker mongodb: docker start -i quantaxis_mgdb_1
def _case_base_op():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    dblist = myclient.list_database_names()
    print(dblist)

    db_quantaxis = myclient['quantaxis']
    collections = db_quantaxis.list_collection_names()
    print(collections)

    for name in collections:
        col = db_quantaxis[name]
        one = col.find_one()
        print('%s: %s\n' % (name, one))

def _case_stock_day(code_list):
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    db_quantaxis = myclient['quantaxis']
    table = db_quantaxis['stock_day']
    cursor = table.find({'code': {'$in': code_list}})
    res = pd.DataFrame([item for item in cursor])
    res = res.assign(
        volume=res.vol,
        date=pd.to_datetime(res.date)
    ).drop_duplicates((['date', 'code'])
    ).query('volume>1').set_index('date',drop=False)
    res = res.loc[:, [
        'code',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'amount',
        'date'
    ]]
    print(res)



if __name__ == '__main__':
    # _case_base_op()
    code_list = [
        '000400', # 许继电气
        '000723', # 美锦能源
        '002351', # 漫步者
        '002713', # 东易日盛
        '300152', # 科融环境
        '300347', # 泰哥医药
        '300708', # 聚灿光电
        '600864', # 哈投股份
        '601318', # 中国平安
        '601816', # 京沪高铁
        '601828', # 美凯龙
    ]
    _case_stock_day(code_list)