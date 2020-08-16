# coding=utf-8
import _sys_path_append_

import os
import sys
import abc
import numpy
import pandas as pd
import src.lib.constants as ct


class BaseOperator(object):
    """操作"""
    OP_TYPE_TIME = 1 # 按规定次数(每次买入金额=当前剩余资金/(总次数-已操作次数)分批买入
    OP_TYPE_CASH = 2 # 按规定金额分批买入

    def __init__(self,
        init_fund: float,
        op_type: int=OP_TYPE_TIME,
        max_times: int,
        each_amount: float,
        clean_all: bool=True):
        """
        init_fund: 初始资金
        max_times: 分多少次操作
        each_: 每次操作买入多少资金
        acc_times: 每次做多/做空数量
        clean_all: True: 一次性结束手上持仓, False: 分批操作
        """
        self.init_fund = init_fund
        self.op_type = op_type
        if self.op_type = self.OP_TYPE_TIME
            self.max_times = max_times
            self.op_times = 0
        else:
            self.each_amount = each_amount
