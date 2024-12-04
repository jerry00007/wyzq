#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: liujianyu
@Date: 2024/12/4 14:19
@FileName: huice.py
@Description:
"""
import pybroker as pb
from pybroker import Strategy, ExecContext
from pybroker.ext.data import AKShare
import akshare as ak
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pandas as pd

# 定义全局参数
pb.param(name='stock_code', value='600000')
pb.param(name='percent', value=1)
pb.param(name='stop_loss_pct', value=10)
pb.param(name='stop_profit_pct', value=10)

# 初始化 AKShare 数据源
akshare = AKShare()

# 定义函数：获取上一个交易日
def get_previous_trading_day():
    calendar = mcal.get_calendar('XSHG')
    today = datetime.today().date()
    trading_days = calendar.valid_days(start_date=today - timedelta(days=7), end_date=today)
    previous_trading_day = trading_days[-2]
    return previous_trading_day.strftime('%Y%m%d')

# 定义函数：获取指定日期的涨停股票池
def get_zt_stocks_by_day(date):
    return ak.stock_zt_pool_em(date=date)

# 定义函数：筛选连板数为 2 的股票
def filter_consecutive_zt_stocks(df):
    if '连板数' in df.columns:
        return df[df['连板数'] == 2]
    else:
        return pd.DataFrame()

# 定义策略函数：买入并设置止盈止损
def buy_with_stop_loss(ctx: ExecContext):
    selected_stocks = pb.param(name='selected_stocks')  # 从参数中获取选中的股票
    pos = ctx.long_pos()

    if not pos and selected_stocks:
        # 计算目标股票数量，根据 'percent' 参数确定应购买的股票数量
        ctx.buy_shares = ctx.calc_target_shares(pb.param(name='percent'))
        ctx.hold_bars = 100
        ctx.selected_stock = selected_stocks[0]  # 买入选中的第一只股票
    else:
        ctx.sell_shares = pos.shares
        # 设置止盈点位，根据 'stop_profit_pct' 参数确定止盈点位
        ctx.stop_profit_pct = pb.param(name='stop_profit_pct')

# 创建策略配置
my_config = pb.StrategyConfig(initial_cash=500000)

# 获取上一个交易日
previous_trading_day = get_previous_trading_day()
print(f"上一个交易日: {previous_trading_day}")

# 获取上一个交易日的涨停股票池数据
stock_zt_df = get_zt_stocks_by_day(previous_trading_day)

# 如果数据为空，直接返回
if stock_zt_df.empty:
    print("没有涨停股票数据。")
    exit()

# 筛选出连板数为 2 的股票
consecutive_zt_stocks = filter_consecutive_zt_stocks(stock_zt_df)

if consecutive_zt_stocks.empty:
    print("没有连板数为 2 的股票。")
    exit()

# 按封板资金降序排列并选出前三只股票
consecutive_zt_stocks_sorted = consecutive_zt_stocks.sort_values(by='封板资金', ascending=False)
top_3_stocks = consecutive_zt_stocks_sorted.head(3)

# 打印选出的股票
print(f"选出的连板数为 2 的前三只股票：")
print(top_3_stocks[['代码', '名称', '连板数', '封板资金']])

# 将选出的股票代码作为参数传递给策略
pb.param(name='selected_stocks', value=top_3_stocks['代码'].tolist())

# 创建策略对象，并添加执行策略函数
strategy = Strategy(akshare, start_date='20240101', end_date='20241203', config=my_config)
strategy.add_execution(fn=buy_with_stop_loss, symbols=top_3_stocks['代码'].tolist())

# 执行回测并输出结果
result = strategy.backtest()
print(result.metrics_df.round(4))

# 中文解释
print("\n回测结果解释：")
metrics = result.metrics_df

# 交易次数
trade_count = metrics[metrics['name'] == 'trade_count']['value'].values[0]
print(f"交易次数 (trade_count): {trade_count} 次")

# 初始市值与结束市值
initial_market_value = metrics[metrics['name'] == 'initial_market_value']['value'].values[0]
end_market_value = metrics[metrics['name'] == 'end_market_value']['value'].values[0]
print(f"初始市值 (initial_market_value): {initial_market_value} 元")
print(f"结束市值 (end_market_value): {end_market_value} 元")

# 总盈亏
total_pnl = metrics[metrics['name'] == 'total_pnl']['value'].values[0]
print(f"总盈亏 (total_pnl): {total_pnl} 元")

# 未实现盈亏
unrealized_pnl = metrics[metrics['name'] == 'unrealized_pnl']['value'].values[0]
print(f"未实现盈亏 (unrealized_pnl): {unrealized_pnl} 元")

# 总回报率
total_return_pct = metrics[metrics['name'] == 'total_return_pct']['value'].values[0]
print(f"总回报率 (total_return_pct): {total_return_pct} %")

# 总盈利和总亏损
total_profit = metrics[metrics['name'] == 'total_profit']['value'].values[0]
total_loss = metrics[metrics['name'] == 'total_loss']['value'].values[0]
print(f"总盈利 (total_profit): {total_profit} 元")
print(f"总亏损 (total_loss): {total_loss} 元")

# 总手续费
total_fees = metrics[metrics['name'] == 'total_fees']['value'].values[0]
print(f"总手续费 (total_fees): {total_fees} 元")

# 最大回撤
max_drawdown = metrics[metrics['name'] == 'max_drawdown']['value'].values[0]
max_drawdown_pct = metrics[metrics['name'] == 'max_drawdown_pct']['value'].values[0]
print(f"最大回撤 (max_drawdown): {max_drawdown} 元")
print(f"最大回撤比例 (max_drawdown_pct): {max_drawdown_pct} %")

# 胜率与亏损率
win_rate = metrics[metrics['name'] == 'win_rate']['value'].values[0]
loss_rate = metrics[metrics['name'] == 'loss_rate']['value'].values[0]
print(f"胜率 (win_rate): {win_rate} %")
print(f"亏损率 (loss_rate): {loss_rate} %")

# 盈利交易与亏损交易次数
winning_trades = metrics[metrics['name'] == 'winning_trades']['value'].values[0]
losing_trades = metrics[metrics['name'] == 'losing_trades']['value'].values[0]
print(f"盈利交易次数 (winning_trades): {winning_trades} 次")
print(f"亏损交易次数 (losing_trades): {losing_trades} 次")

# 平均盈亏
avg_pnl = metrics[metrics['name'] == 'avg_pnl']['value'].values[0]
print(f"平均盈亏 (avg_pnl): {avg_pnl} 元")

# 平均回报率
avg_return_pct = metrics[metrics['name'] == 'avg_return_pct']['value'].values[0]
print(f"平均回报率 (avg_return_pct): {avg_return_pct} %")

# 平均持仓周期
avg_trade_bars = metrics[metrics['name'] == 'avg_trade_bars']['value'].values[0]
print(f"平均持仓周期 (avg_trade_bars): {avg_trade_bars} 个交易日")

# 平均盈利与亏损
avg_profit = metrics[metrics['name'] == 'avg_profit']['value'].values[0]
avg_loss = metrics[metrics['name'] == 'avg_loss']['value'].values[0]
print(f"平均盈利 (avg_profit): {avg_profit} 元")
print(f"平均亏损 (avg_loss): {avg_loss} 元")

# 最大盈利与最大亏损
largest_win = metrics[metrics['name'] == 'largest_win']['value'].values[0]
largest_loss = metrics[metrics['name'] == 'largest_loss']['value'].values[0]
print(f"最大盈利 (largest_win): {largest_win} 元")
print(f"最大亏损 (largest_loss): {largest_loss} 元")

# 最大连续盈利与亏损
max_wins = metrics[metrics['name'] == 'max_wins']['value'].values[0]
max_losses = metrics[metrics['name'] == 'max_losses']['value'].values[0]
print(f"最大连续盈利 (max_wins): {max_wins} 次")
print(f"最大连续亏损 (max_losses): {max_losses} 次")

# 夏普比率与索提诺比率
sharpe = metrics[metrics['name'] == 'sharpe']['value'].values[0]
sortino = metrics[metrics['name'] == 'sortino']['value'].values[0]
print(f"夏普比率 (sharpe): {sharpe}")
print(f"索提诺比率 (sortino): {sortino}")

# 盈利因子
profit_factor = metrics[metrics['name'] == 'profit_factor']['value'].values[0]
print(f"盈利因子 (profit_factor): {profit_factor}")

# 溃疡指数与资金曲线 R²
ulcer_index = metrics[metrics['name'] == 'ulcer_index']['value'].values[0]
equity_r2 = metrics[metrics['name'] == 'equity_r2']['value'].values[0]
print(f"溃疡指数 (ulcer_index): {ulcer_index}")
print(f"资金曲线 R² (equity_r2): {equity_r2}")

# 标准误差
std_error = metrics[metrics['name'] == 'std_error']['value'].values[0]
print(f"标准误差 (std_error): {std_error} 元")