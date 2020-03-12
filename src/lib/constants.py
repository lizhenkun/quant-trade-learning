# coding=utf-8
import os
PRJ_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(PRJ_HOME), 'data')
CHINA_STOCK_DATA_DIR = os.path.join(DATA_DIR, 'china/stock')

STOCK_COLS = ['datetime', 'open', 'high', 'low', 'close', 'vol', 'amount']