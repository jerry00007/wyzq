import akshare as ak
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pandas as pd


def get_trading_days(start_date, end_date):
    """获取指定时间范围内的交易日"""
    calendar = mcal.get_calendar('XSHG')  # 上海证券交易所
    trading_days = calendar.valid_days(start_date=start_date, end_date=end_date)
    return [day.strftime('%Y%m%d') for day in trading_days]


def get_zt_stocks_by_day(date):
    """获取指定交易日的涨停股票池"""
    try:
        return ak.stock_zt_pool_em(date=date)
    except Exception as e:
        print(f"获取 {date} 涨停股票数据失败: {e}")
        return pd.DataFrame()


def filter_consecutive_zt_stocks(df, target_consecutive):
    """筛选指定连板数的股票"""
    if '连板数' in df.columns:
        return df[df['连板数'] == target_consecutive]
    else:
        return pd.DataFrame()  # 如果没有连板数列，返回空 DataFrame


def process_date_range(start_date, end_date):
    """处理时间范围内的数据"""
    trading_days = get_trading_days(start_date, end_date)
    successful_stocks = []  # 晋级3连板的股票
    unsuccessful_stocks = []  # 未晋级的股票

    for i in range(len(trading_days) - 1):  # 遍历时间范围内的交易日
        current_day = trading_days[i]
        next_day = trading_days[i + 1]

        print(f"正在处理日期: {current_day}")

        # 获取当日涨停股票数据
        stock_zt_df = get_zt_stocks_by_day(current_day)
        if stock_zt_df.empty:
            print(f"{current_day} 无涨停股票数据，跳过。")
            continue

        # 筛选昨日2连板的股票
        two_limit_up_stocks = filter_consecutive_zt_stocks(stock_zt_df, target_consecutive=2)
        if two_limit_up_stocks.empty:
            print(f"{current_day} 没有连续2日涨停的股票，跳过。")
            continue

        # 获取次日涨停数据
        next_day_zt_df = get_zt_stocks_by_day(next_day)
        if next_day_zt_df.empty:
            print(f"{next_day} 无涨停股票数据，无法判断晋级情况。")
            continue

        # 判断哪些股票晋级为3连板
        for _, stock in two_limit_up_stocks.iterrows():
            stock_code = stock['代码']
            stock_name = stock['名称']

            # 判断是否在次日3连板股票中
            is_successful = not next_day_zt_df[
                (next_day_zt_df['代码'] == stock_code) &
                (next_day_zt_df['连板数'] == 3)
            ].empty

            stock_data = stock.to_dict()
            stock_data['2连板日期'] = current_day  # 添加2连板日期
            if is_successful:
                successful_stocks.append(stock_data)
            else:
                unsuccessful_stocks.append(stock_data)

    # 保存结果到文件
    pd.DataFrame(successful_stocks).to_csv("晋级3连板股票.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(unsuccessful_stocks).to_csv("未晋级股票.csv", index=False, encoding="utf-8-sig")
    print("数据已保存完成。")


if __name__ == "__main__":
    # 输入时间范围
    start_date = "2024-11-01"
    end_date = "2024-12-03"

    process_date_range(start_date, end_date)
