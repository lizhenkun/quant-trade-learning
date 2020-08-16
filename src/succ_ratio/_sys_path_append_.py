# coding=utf-8

import os
import sys
file_abs = os.path.abspath(__file__)
index = file_abs.find('/src/')
sys.path.append(file_abs[:index])