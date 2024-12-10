#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: liujianyu
@Date: 2024/12/9 18:50
@FileName: yuce.py
@Description: 
"""
import pandas as pd
import akshare as ak
import talib as ta
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import shap
import matplotlib.pyplot as plt

# 假设数据已经加载到dataframe中，包含了2连板的股票数据
# 示例： df_2_lianban = pd.read_csv('2连板股票数据.csv')

def add_technical_indicators(data):
    """生成常用的技术指标"""
    data['ma_5'] = ta.SMA(data['收盘价'], timeperiod=5)
    data['ma_20'] = ta.SMA(data['收盘价'], timeperiod=20)
    data['rsi'] = ta.RSI(data['收盘价'], timeperiod=14)
    data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['收盘价'], fastperiod=12, slowperiod=26, signalperiod=9)
    data['boll_up'], data['boll_mid'], data['boll_low'] = ta.BBANDS(data['收盘价'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    return data

def preprocess_data(df):
    """预处理数据，生成所有特征"""
    df = add_technical_indicators(df)
    df['是否晋级'] = (df['连板数'] == 3).astype(int)  # 标记是否晋级为3连板
    return df

def train_model(df):
    """训练XGBoost模型"""
    X = df.drop(columns=['是否晋级', '日期'])  # 特征
    y = df['是否晋级']  # 目标变量

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # 模型评估
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    print(f"模型准确率: {accuracy}")
    print(f"AUC: {auc}")
    return model, X_test, y_test

def explain_model(model, X_test):
    """使用SHAP解释模型"""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    shap.summary_plot(shap_values, X_test)

# 假设从文件读取2连板数据
df_2_lianban = pd.read_csv('2连板股票数据.csv')

# 预处理数据，生成特征
preprocessed_data = preprocess_data(df_2_lianban)

# 训练模型
model, X_test, y_test = train_model(preprocessed_data)

# 使用SHAP解释模型
explain_model(model, X_test)

# 获取晋级到3连板的股票
df_jinji_3_lianban = preprocessed_data[preprocessed_data['是否晋级'] == 1]

# 获取未晋级3连板的股票
df_weijinji_3_lianban = preprocessed_data[preprocessed_data['是否晋级'] == 0]

# 保存晋级3连板和未晋级3连板的股票数据
df_jinji_3_lianban.to_csv('晋级3连板股票数据.csv', index=False)
df_weijinji_3_lianban.to_csv('未晋级3连板股票数据.csv', index=False)

# 保存特征工程数据
preprocessed_data.to_csv('2连板股票数据_特征.csv', index=False)

# 保存训练后的模型
model.save_model('xgb_model.json')

# 保存SHAP结果图
shap.summary_plot(shap_values, X_test, show=False)
plt.savefig('shap_summary_plot.png')

print("数据处理完成，模型保存成功，SHAP图已保存！")
