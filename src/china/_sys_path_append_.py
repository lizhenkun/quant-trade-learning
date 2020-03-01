#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
print('__import__ begin')
print('\n'.join(sys.path))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))
print('\n'.join(sys.path))
print('__import__ end')