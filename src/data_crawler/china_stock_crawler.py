# coding=utf-8
import os
import sys
import argparse

if not __package__:
    import _sys_path_append_

import src.lib.data_helper as DataHelper
import src.data_crawler.tdx.pytdx_stock_crawler as StockCrawler

try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor > 5
except AssertionError:
    raise RuntimeError('requires Python 3.6+!')


def add_argparse() -> object:
    """add argument parser
    Returns:
    argparse.Namespace object
    """
    parser = argparse.ArgumentParser(
        usage='pyton %s -c stock_code -f frequent' % os.path.basename(__file__)
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-c', '--code', required=True, help='china stock code, such as 600519', type=str)
    parser.add_argument('-f', '--freq', default='day', help='period frequent, 1min, 5min, 15min, 30min, 60min, day, week, season, year', type=str)
    args = parser.parse_args()
    return args


def crawl_china_stock(argv):
    args = add_argparse()
    print(args)
    # stock_df = StockCrawler.download_history_data(
    #     args.code, args.freq
    # )
    stock_df = StockCrawler.download_history_fq_data(args.code)
    file_path = DataHelper.save_data(stock_df, args.code, args.freq)
    print('save to file: %s' % file_path)


if __name__ == '__main__':
    sys.exit(crawl_china_stock(sys.argv))