#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: liujianyu
@Date: 2024/12/3 13:22
@FileName: bankuai.py
@Description: 
"""
import akshare as ak
import pandas as pd

# 获取数据
stock_board_concept_name_em_df = ak.stock_board_concept_name_em()

# 检查“上涨家数”这一列是否存在于DataFrame中
if "上涨家数" in stock_board_concept_name_em_df.columns:
    # 根据“上涨家数”列进行降序排列
    stock_board_concept_name_em_df_sorted = stock_board_concept_name_em_df.sort_values(by="上涨家数", ascending=False)

    # 提取前五个“板块名称”
    top_5_concepts = stock_board_concept_name_em_df_sorted.head(5)["板块名称"].tolist()

    # 对每个板块名称进行成分股查询，并只取前五个成分股
    for concept in top_5_concepts:
        print(f"查询板块：{concept}")
        stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol=concept)

        # 只取前五个成分股
        top_5_stocks = stock_board_concept_cons_em_df.head(5)

        # 打印前五个成分股
        print(top_5_stocks)
else:
    print("DataFrame中没有找到‘上涨家数’这一列")

# stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol="车联网")
# print(stock_board_concept_cons_em_df)