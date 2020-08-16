# coding=utf-8
import os
PRJ_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(PRJ_HOME), 'data')
CHINA_STOCK_DATA_DIR = os.path.join(DATA_DIR, 'china/stock')
STATIC_DIR = os.path.join(os.path.dirname(PRJ_HOME), 'static')
HTML_DIR = os.path.join(STATIC_DIR, 'html')

STOCK_COLS = ['datetime', 'open', 'high', 'low', 'close', 'vol', 'amount']