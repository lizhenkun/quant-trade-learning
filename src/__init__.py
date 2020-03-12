# coding=utf-8
import os
import sys
sys.path.append(os.path.abspath('..'))
import src.lib.constants as ct

if not os.path.exists(ct.CHINA_STOCK_DATA_DIR):
    os.makedirs(ct.CHINA_STOCK_DATA_DIR)