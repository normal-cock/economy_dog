import os
import time
import datetime
import numpy as np
import akshare as ak  # TODO 增加本地缓存
from metric.stock_data.metrc_util import (
    sort_by_date,
    parse_money_num_with_unit,
    cache_adapter,
)

ak.stock_us_spot_em = cache_adapter(ak.stock_us_spot_em)


def get_stock_dv_detail(symbol):
    df = ak.stock_a_indicator_lg(symbol=symbol)
    print(df)
    stock_fhps_detail_em_df = None
    try:
        stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol=symbol)
    except Exception as e:
        print(f"got exception {e}")
        return
    else:
        print(
            stock_fhps_detail_em_df[
                [
                    "报告期",
                    "业绩披露日期",
                    "现金分红-股息率",
                    "每股未分配利润",
                    "现金分红-现金分红比例描述",
                ]
            ]
        )
        print(stock_fhps_detail_em_df.iloc[0])
        print(stock_fhps_detail_em_df.iloc[1])


def get_stock_dv(trading_date, symbol, current_price):
    df = None
    try:
        df = ak.stock_a_indicator_lg(symbol=symbol)
    except Exception as e:
        print(e)
        return np.nan
    last_stock_dv_info = df.loc[df["trade_date"] == trading_date].iloc[0]
    if np.isnan(last_stock_dv_info["dv_ttm"]):
        stock_fhps_detail_em_df = None
        try:
            stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol=symbol)
        except Exception as e:
            print(e)
            return np.nan
        begin_date = datetime.date(year=trading_date.year - 1, month=1, day=1)
        end_date = datetime.date(year=trading_date.year - 1, month=12, day=31)
        last_year_fhps_list = stock_fhps_detail_em_df.loc[
            (stock_fhps_detail_em_df["报告期"] >= begin_date)
            & (stock_fhps_detail_em_df["报告期"] <= end_date)
        ]
        if len(last_year_fhps_list) == 0:
            return 0
        return round(
            100
            * sum(last_year_fhps_list["现金分红-现金分红比例"])
            / 10
            / current_price,
            4,
        )
    return last_stock_dv_info["dv_ttm"]


# 股息率
def get_stock_dv_v2(trading_date, symbol, current_price):
    stock_fhps_detail_em_df = None
    try:
        stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol=symbol)
    except Exception as e:
        print(e)
        return np.nan
    begin_date = datetime.date(
        year=trading_date.year - 1, month=trading_date.month, day=trading_date.day
    )
    end_date = trading_date
    last_year_fhps_list = stock_fhps_detail_em_df.loc[
        (stock_fhps_detail_em_df["报告期"] >= begin_date)
        & (stock_fhps_detail_em_df["报告期"] <= end_date)
    ]
    if len(last_year_fhps_list) == 0:
        return 0
    return round(
        100 * sum(last_year_fhps_list["现金分红-现金分红比例"]) / 10 / current_price, 4
    )


# dividend payout ratio 股利支付率。不包括今年
def get_last_n_year_dp(trading_date, symbol, n=10):
    """
    return dp, err_string
    """
    if not (1 <= n <= 10):
        return 0, "invalid n"
    # 获取过去n年分红总金额
    df1 = None
    try:
        df1 = ak.stock_fhps_detail_em(symbol=symbol)
    except Exception as e:
        return 0, f"get share amount error: {str(e)}"
    begin_date = datetime.date(year=trading_date.year - n, month=1, day=1)
    end_date = datetime.date(year=trading_date.year - 1, month=12, day=31)
    last_n_year_fhps_list = df1.loc[
        (df1["报告期"] >= begin_date) & (df1["报告期"] <= end_date)
    ][["报告期", "业绩披露日期", "现金分红-现金分红比例", "现金分红-现金分红比例描述", "总股本"]]
    if len(last_n_year_fhps_list) < n:
        return (
            0,
            f"n={n}||share_time={len(last_n_year_fhps_list)}||not enough share time",
        )
    total_share_amount = 0
    for _, row in last_n_year_fhps_list.iterrows():
        share_amount = row["现金分红-现金分红比例"] * row["总股本"] / 10
        if np.isnan(share_amount):
            continue
        total_share_amount += share_amount

    # 获取过去n年归母利润总金额
    df2 = None
    try:
        df2 = ak.stock_financial_abstract(symbol=symbol)
    except Exception as e:
        return 0, f"get interest error: {str(e)}"
    date_list = []
    for i in range(n):
        tmp_year = trading_date.year - n + i
        date_list.append(f"{tmp_year}1231")
    interest_s = df2[df2["指标"] == "归母净利润"].iloc[0][date_list]
    if len(interest_s) != n:
        return 0, f"n={n}||interest_time={len(interest_s)}||no enough interest"
    total_interest = sum(interest_s)
    if total_interest <= 0:
        return 0, "empty interest"
    return round(100 * total_share_amount / total_interest, 4), ""


# dividend payout ratio 股利支付率。不包括今年
@sort_by_date
def get_last_n_year_dp_p50(trading_date, symbol, n=10):
    """
    return dp, err_string
    """
    if not (1 <= n <= 10):
        return 0, "invalid n"
    df = None
    try:
        df = ak.stock_fhps_detail_ths(symbol=symbol)
    except Exception as e:
        return 0, f"get share amount error: {str(e)}"
    begin_str = f"{trading_date.year-n}"
    end_str = f"{trading_date.year}"
    last_n_year_list = df.loc[
        (df["报告期"] >= begin_str)
        & (df["报告期"] < end_str)
        & (df["股利支付率"].str.contains("%"))
    ][["报告期", "分红方案说明", "股利支付率"]]
    last_n_year_s = last_n_year_list["股利支付率"].map(lambda x: float(x[:-2]))
    if len(last_n_year_s) < n:
        return 0, f"n={n}||share_time={len(last_n_year_s)}||no enough share time"
    return last_n_year_s.quantile(0.5), ""


@sort_by_date
def get_stock_interest_yearly_a(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按年度")
    df = df[["报告期", "净利润"]]
    df.loc[:, "date"] = df.apply(
        lambda x: datetime.date(year=x["报告期"], month=12, day=31), axis=1
    )
    df.loc[:, "value"] = df.apply(
        lambda x: parse_money_num_with_unit(x["净利润"]), axis=1
    )
    df.loc[:, "unit"] = "人民币"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_interest_yearly_hk(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_hk_report_em(
        stock=symbol,
        symbol="利润表",
        indicator="年度",  # 这里获取ROE数据，包含净利润信息
    )
    df = df[df["STD_ITEM_NAME"].isin(("股东应占溢利",))]
    # 从2023-12-31 00:00:00格式字符串生成datetime.date
    df.loc[:, "date"] = df["REPORT_DATE"].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    )
    df.loc[:, "value"] = df["AMOUNT"]
    df.loc[:, "unit"] = "人民币"

    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_interest_yearly_us(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_us_analysis_indicator_em(symbol=symbol, indicator="年报")
    # df = ak.stock_financial_us_report_em(
    #     stock=symbol, symbol="综合损益表", indicator="年报"
    # )
    df.loc[:, "date"] = df["REPORT_DATE"].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    )
    df.loc[:, "value"] = df["PARENT_HOLDER_NETPROFIT"]
    df.loc[:, "unit"] = "美元"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_equity_yearly_a(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_debt_ths(symbol=symbol, indicator="按年度")
    df = df[["报告期", "所有者权益（或股东权益）合计"]]
    df.loc[:, "date"] = df.apply(
        lambda x: datetime.date(year=x["报告期"], month=12, day=31), axis=1
    )
    # df.loc[:, 'value'] = df.apply(parse_money_num_with_unit, axis=1)
    df.loc[:, "value"] = df.apply(
        lambda x: parse_money_num_with_unit(x["所有者权益（或股东权益）合计"]), axis=1
    )
    df.loc[:, "unit"] = "人民币"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_equity_yearly_hk(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_hk_report_em(
        stock=symbol,
        symbol="资产负债表",
        indicator="年度",  # 这里获取ROE数据，包含净利润信息
    )
    df = df[df["STD_ITEM_NAME"].isin(("总权益",))]
    df.loc[:, "date"] = df["REPORT_DATE"].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    )
    df.loc[:, "value"] = df["AMOUNT"]
    df.loc[:, "unit"] = "人民币"

    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_equity_yearly_us(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_financial_us_report_em(
        stock=symbol, symbol="资产负债表", indicator="年报"
    )
    df = df[df["ITEM_NAME"].isin(("股东权益合计",))]
    # print(df)
    # print(df.iloc[0])
    # print(df.columns)
    df.loc[:, "date"] = df.loc[:, "REPORT_DATE"].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    )
    df.loc[:, "value"] = df.loc[:, "AMOUNT"]
    df.loc[:, "unit"] = "美元"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_ttm_pe_a(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_value_em(symbol=symbol)
    df = df.copy()
    df.loc[:, "date"] = df.loc[:, "数据日期"]
    df.loc[:, "value"] = df.loc[:, "PE(TTM)"]
    df.loc[:, "unit"] = "None"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_stock_ttm_pe_hk(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_hk_valuation_baidu(
        symbol=symbol, indicator="市盈率(TTM)", period="近一年"
    )
    df = df.copy()
    df.loc[:, "unit"] = "None"
    return df


@sort_by_date
def get_stock_ttm_pe_us(symbol):
    """
    TODO 暂未成功实现，先用get_latest_ttm_pe_us替代
    symbol不用加交易所前缀, 如sz, sh"""
    # 接口会报错
    df = ak.stock_us_daily(
        symbol=symbol,
        # start_date="20200101",
        # end_date="20231231",
        adjust="",
    )
    print(df)
    print(df.iloc[0])
    print(df.columns)
    # print(df[["日期", "总市值", "市盈率TTM"]])
    # 获取美股实时行情数据
    df = ak.stock_us_famous_spot_em(symbol="科技类")
    print(df.iloc[0])
    df = ak.stock_us_spot_em()
    print(df.iloc[0])
    # df = ak.stock_hk_valuation_baidu(
    #     symbol=symbol, indicator="市盈率(TTM)", period="近一年"
    # )
    df.loc[:, "unit"] = "None"
    return df


def get_latest_ttm_pe_a(symbol):
    df = get_stock_ttm_pe_a(symbol)
    return df.iloc[:1]


def get_latest_ttm_pe_hk(symbol):
    df = get_stock_ttm_pe_hk(symbol)
    return df.iloc[:1]


def get_latest_ttm_pe_us(symbol):
    today = datetime.date.today()
    df = ak.stock_us_spot_em()
    df = df[df["代码"].str.endswith("." + symbol)]
    df = df.copy()
    df.loc[:, "date"] = today
    df.loc[:, "value"] = df.loc[:, "市盈率"]
    df.loc[:, "unit"] = "None"
    return df[["date", "value", "unit"]]


def get_latest_market_value_a(symbol):
    df = stock_market_value_a(symbol=symbol)
    return df.iloc[:1]


def get_latest_market_value_hk(symbol):
    df = stock_market_value_hk(symbol=symbol)
    return df.iloc[:1]


def get_latest_market_value_us(symbol):
    today = datetime.date.today()
    df = ak.stock_us_spot_em()
    df = df[df["代码"].str.endswith("." + symbol)]
    df = df.copy()
    df.loc[:, "date"] = today
    df.loc[:, "value"] = df.loc[:, "总市值"]
    df.loc[:, "unit"] = "美元"
    return df[["date", "value", "unit"]]


@sort_by_date
def stock_market_value_a(symbol):
    """symbol不用加交易所前缀, 如sz, sh"""
    df = ak.stock_a_indicator_lg(symbol=symbol)
    df = df.copy()
    df.loc[:, "date"] = df.loc[:, "trade_date"]
    df.loc[:, "value"] = df.loc[:, "total_mv"] * 10000
    df.loc[:, "unit"] = "人民币"
    return df[["date", "value", "unit"]]
    print(df)
    print(df.columns)
    # df.loc[:, 'date'] = df['数据日期']
    # df.loc[:, 'value'] = df['总市值']


@sort_by_date
def stock_market_value_hk(symbol):
    """symbol不需要加交易所前缀,如hk"""
    df = ak.stock_hk_valuation_baidu(symbol=symbol, indicator="总市值", period="近一年")
    df = df.copy()
    df.loc[:, "date"] = df["date"]
    # 正常是港币
    df.loc[:, "value"] = df["value"] * 10000 * 10000 * get_close_price_hk()
    df.loc[:, "unit"] = "人民币"
    return df[["date", "value", "unit"]]


@sort_by_date
def get_close_price_a(symbol, start_date, end_date, adjust=None):
    """获取收盘价"""
    """adjust None, qfq, hfq"""
    df = ak.stock_zh_a_hist_tx(
        symbol=symbol,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        adjust="qfq",
    )
    df.loc[:, "date"] = df["date"]
    df.loc[:, "value"] = df["close"]
    df.loc[:, "unit"] = "人民币"
    return df[["date", "value", "unit"]]
    print(df)
    print(df.columns)


# 获取港币兑人民币汇率数据
def get_close_price_hk(start_date=None, end_date=None):
    """获取港币的汇率"""
    if start_date == None:
        start_date = datetime.date.today() - datetime.timedelta(days=15)
    if end_date == None:
        end_date = datetime.date.today()
    df = ak.currency_boc_sina(
        symbol="港币",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
    )
    df = df.sort_values(by="日期", ascending=False)
    return df.iloc[0]["中行汇买价"] / 100


def test():
    
    print(get_latest_ttm_pe_us("KO"))
    print(get_latest_market_value_us("KO"))
    # 获取港币兑人民币汇率数据
    # print(get_stock_ttm_pe_a("000651"))
    # print(get_stock_ttm_pe_hk("00883"))
    # print(get_stock_interest_yearly_hk("00883"))
    # print(get_stock_interest_yearly_hk('00700'))
    # print(get_close_price(
    #     symbol = 'sz000651',
    #     start_date = datetime.date(2022, 5, 5),
    #     end_date = datetime.date(2023, 5, 5)))
    # last_trading_date = datetime.date(2023, 5, 5)
    # symbol = '000651'
    # print(get_last_n_year_dp(last_trading_date, symbol, 10))
    # print(get_last_n_year_dp_p50(last_trading_date, symbol, 10))
    # # get_stock_dv_detail(symbol='000651')
    # os._exit(0)


if __name__ == "__main__":
    test()
    # last_trading_date = datetime.date(2023, 5, 5)
    # stock_list_df = ak.stock_zh_a_spot_em()
    # for index, stock in stock_list_df.iterrows():
    #     stock_symbol = stock['代码']
    #     stock_name = stock['名称']
    #     stock_total_mv = stock['总市值']
    #     stock_last_price = stock['昨收']
    #     stock_60d_increase = stock['60日涨跌幅']

    #     if stock_total_mv > 500*10000*10000 and stock_symbol not in []:
    #         # last_stock_dv = get_stock_dv(last_trading_date, stock_symbol, stock_last_price)
    #         last_stock_dv = get_stock_dv_v2(last_trading_date, stock_symbol, stock_last_price)
    #         # 获取分红报告列表崩溃的。均是未派现
    #         if np.isnan(last_stock_dv):
    #             # get_stock_dv_detail(symbol=stock_symbol)
    #             print(index, stock_name, stock_symbol, 'dv is nan')
    #             print('\n')
    #             continue
    #         if last_stock_dv >= 7:
    #             print(index, stock_name, stock_symbol, stock_total_mv/10000/10000, stock_60d_increase)
    #             print(f'current dv is: {last_stock_dv}')
    #             print(get_last_n_year_dp(last_trading_date, stock_symbol, 7))
    #             print(get_last_n_year_dp_p50(last_trading_date, stock_symbol, 7))
    #             print('\n')
    #         time.sleep(2)
