import akshare as ak
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pandas as pd

def get_previous_trading_day():
    """获取上一个交易日"""
    # 获取交易日历
    calendar = mcal.get_calendar('XSHG')  # 上海证券交易所
    # 获取最近的 2 个有效交易日
    today = datetime.today().date()
    trading_days = calendar.valid_days(start_date=today - timedelta(days=7), end_date=today)
    # 获取最近的前一个交易日
    previous_trading_day = trading_days[-2]  # 倒数第二个交易日
    return previous_trading_day.strftime('%Y%m%d')  # 返回日期格式为 'YYYYMMDD'

def get_zt_stocks_by_day(date):
    """获取指定交易日的涨停股票池"""
    return ak.stock_zt_pool_em(date=date)

def filter_consecutive_zt_stocks(df):
    """筛选连板数为 2 的股票"""
    if '连板数' in df.columns:
        return df[df['连板数'] == 2]  # 筛选连板数为 2 的股票
    else:
        return pd.DataFrame()  # 如果没有连板数列，返回空 DataFrame

def main():
    # 获取上一个交易日
    previous_trading_day = get_previous_trading_day()
    print(f"上一个交易日: {previous_trading_day}")

    # 获取上一个交易日的涨停股票池数据
    stock_zt_df = get_zt_stocks_by_day(previous_trading_day)

    # 如果数据为空，直接返回
    if stock_zt_df.empty:
        print("没有涨停股票数据。")
        return

    # 筛选出连板数为 2 的股票
    consecutive_zt_stocks = filter_consecutive_zt_stocks(stock_zt_df)

    if consecutive_zt_stocks.empty:
        print("没有连板数为 2 的股票。")
        return

    # 按封板资金降序排列
    consecutive_zt_stocks_sorted = consecutive_zt_stocks.sort_values(by='封板资金', ascending=False)

    # 输出筛选后的股票（包含代码、名称、连板数）
    print(f"上一个交易日（{previous_trading_day}）连板数为 2 的股票（按封板资金降序排列）：")
    print(consecutive_zt_stocks_sorted[['代码', '名称', '连板数', '封板资金', '炸板次数', '涨停统计']])

    # 用于存储每只股票的代码、名称、涨跌幅
    stock_info = []

    # 获取这些股票的今日行情，并保存涨跌幅
    for stock_code, stock_name in zip(consecutive_zt_stocks_sorted['代码'], consecutive_zt_stocks_sorted['名称']):
        try:
            stock_data = ak.stock_bid_ask_em(symbol=stock_code)
            if stock_data.empty:
                print(f"股票 {stock_code} ({stock_name}) 无今日行情数据。")
                continue

            # 获取相关字段
            current_data = {
                "涨跌幅": stock_data.loc[22, 'value'] if len(stock_data) > 22 else None,
                "换手率": stock_data.loc[26, 'value'] if len(stock_data) > 26 else None,
                "量比": stock_data.loc[27, 'value'] if len(stock_data) > 27 else None,
            }

            # 保存股票的代码、名称和涨跌幅
            stock_info.append({
                "代码": stock_code,
                "名称": stock_name,
                "涨跌幅": current_data["涨跌幅"],
            })

        except Exception as e:
            print(f"获取股票 {stock_code} ({stock_name}) 行情数据失败: {e}")

    # 将数据转为 DataFrame，按涨跌幅升序排序
    if stock_info:
        stock_info_df = pd.DataFrame(stock_info)
        stock_info_df['涨跌幅'] = pd.to_numeric(stock_info_df['涨跌幅'], errors='coerce')  # 转换为数值类型
        sorted_stocks = stock_info_df.sort_values(by='涨跌幅', ascending=True)  # 按涨跌幅升序排序

        print("\n按今日涨跌幅升序排序的股票：")
        print(sorted_stocks[['代码', '名称', '涨跌幅']])

if __name__ == "__main__":
    main()
