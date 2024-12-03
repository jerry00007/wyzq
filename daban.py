#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: liujianyu
@Date: 2024/12/3 15:50
@FileName: qiangshipiao.py
@Description: 
"""
import akshare as ak
from datetime import datetime
import pandas as pd


def main():
    # 获取今天的日期
    today = datetime.today().date().strftime('%Y%m%d')

    # 获取今天的涨停股票数据
    stock_zt_df = ak.stock_zt_pool_em(date=today)

    # 获取当前市场行情
    stocks = ak.stock_zh_a_spot_em()

    # 获取已经涨停的股票代码
    zt_stocks = stock_zt_df['代码'].tolist()

    # 筛选出未涨停的股票
    non_zt_stocks = stocks[~stocks['代码'].isin(zt_stocks)]

    # 按照涨跌幅降序排列
    sorted_by_pct = non_zt_stocks.sort_values(by="涨跌幅", ascending=False)

    # 获取涨跌幅排名前10的主板股票
    mainboard_top10 = sorted_by_pct[sorted_by_pct['代码'].str.startswith('6')].head(10)

    # 输出涨跌幅排序前10的主板股票
    print("主板前10个未涨停的股票（按涨跌幅降序排序）：")
    print(mainboard_top10[['代码', '名称', '涨跌幅', '成交量', '成交额', '换手率']])

    # 按照成交额降序排列
    sorted_by_turnover = non_zt_stocks.sort_values(by="成交额", ascending=False)

    # 获取成交额排名前10的主板股票
    mainboard_top10_by_turnover = sorted_by_turnover[sorted_by_turnover['代码'].str.startswith('6')].head(10)

    # 输出成交额排序前10的主板股票
    print("\n主板前10个未涨停的股票（按成交额降序排序）：")
    print(mainboard_top10_by_turnover[['代码', '名称', '涨跌幅', '成交量', '成交额', '换手率']])


if __name__ == "__main__":
    main()
