import json
from typing import Tuple, List
import datetime
import pandas as pd
import plotly.express as px
from scipy import stats
from jinja2 import Environment, FileSystemLoader
from metric.data_source.sse import (
    get_cur_total_value_4_mainboard_a,
    get_last_trading_day_total_value_4_mainboard_a,
)
from metric.data_source.zhongjing import (
    query_nationwide_annual_gdp,
    query_monthly_total_value_4_mainboard_a,
)
from metric import metric_query
from metric.stock_data.single_stock_info import (
    get_stock_equity_yearly_a,
    get_stock_equity_yearly_hk,
    get_stock_equity_yearly_us,
    get_stock_interest_yearly_a,
    get_stock_interest_yearly_hk,
    get_stock_interest_yearly_us,
    get_latest_market_value_a,
    get_latest_market_value_hk,
    get_latest_market_value_us,
    get_latest_ttm_pe_a,
    get_latest_ttm_pe_hk,
    get_latest_ttm_pe_us,
    get_stock_ttm_pe_a,
    get_stock_ttm_pe_hk,
    stock_market_value_a,
    stock_market_value_hk,
)
from util.email import send_html
from util.log import logger

_CARED_ETF = [""]
jinja_env = Environment(loader=FileSystemLoader("template"))
daily_report_tpl = jinja_env.get_template("daily_report.html")


def _gen_trend_html(df, cur_value):
    std_pct = [0.25, 0.5, 0.75]
    std_pct_value = df["value"].quantile(std_pct)
    fig = px.line(
        x=df["date"],
        y=df["value"],
    )

    for i, pct_value in enumerate(std_pct_value):
        rounded_pct_value = round(pct_value, 2)
        fig.add_hline(
            y=rounded_pct_value,
            line_dash="dash",
            line_color="red",
            line_width=0.8,
            annotation_text=f"{rounded_pct_value} ({int(std_pct[i]*100)}th)",
            annotation_position="top right",
        )

    fig.update_layout(
        xaxis_title=None,  # 隐藏 X 轴标签
        yaxis_title=None,  # 隐藏 Y 轴标签
        width=400,
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),  # 调整边距
        hovermode="x unified",
    )
    return fig.to_html(include_plotlyjs="cdn", full_html=False)


def _gen_column_one_metric(metric_name):
    today = datetime.date.today()
    cur_df = metric_query(
        metric_name=metric_name,
        start_date=today - datetime.timedelta(days=10),
        end_date=today,
    )
    cur_value = cur_df["value"].iloc[0]
    cur_date = cur_df["date"].iloc[0]
    cur_value_html = f"{cur_value} ({cur_date})"

    y10_monthly_df = metric_query(
        metric_name=metric_name,
        start_date=datetime.date(today.year - 10, 1, 1),
        end_date=today,
        aggr_type="quarterly",
    )
    y10_quantile = round(stats.percentileofscore(y10_monthly_df["value"], cur_value), 2)

    y10_quantile_html = f"{y10_quantile}th"
    y10_trend_html = _gen_trend_html(y10_monthly_df, cur_value)

    y50_yearly_df = metric_query(
        metric_name=metric_name,
        start_date=datetime.date(today.year - 50, 1, 1),
        end_date=today,
        aggr_type="yearly",
    )
    print(y50_yearly_df)
    y50_quantile = round(stats.percentileofscore(y50_yearly_df["value"], cur_value), 2)

    y50_quantile_html = f"{y50_quantile}th"
    y50_trend_html = _gen_trend_html(y50_yearly_df, cur_value)

    return (
        cur_value_html,
        y10_quantile_html,
        y10_trend_html,
        y50_quantile_html,
        y50_trend_html,
    )


def get_astock_status_v2() -> str:
    """返回值为html"""
    metrics = {
        "hs300_ttm_pe": "沪深300动态市盈率",
        "gz_cn_y10": "中国10年国债收益率",
        "gz_us_y10": "美国10年国债收益率",
    }
    metric_results = []
    for metric_key, metric_name in metrics.items():
        html_result = _gen_column_one_metric(metric_key)
        metric_results.append([metric_name, *html_result])

    rendered_html = daily_report_tpl.render(metrics=metric_results)
    print(rendered_html)


def get_astock_status() -> Tuple[str, List, str]:
    """
    return cur_trade_date, monthly_data_list, err_string
    list元素为{
        'date' # 日期，2022-10
        'gdp' # 去年gdp
        'astock' # 当月A股总市值
        'proportion' # round(100*astock/gdp, 2)
    }
    """
    monthly_data_list = []
    cur_trade_date = ""
    cur_mainboard_a_value = 0
    annual_gdp_data_dict = {}
    tmp_result, err_string = get_cur_total_value_4_mainboard_a()
    if len(err_string) != 0:
        return (
            cur_trade_date,
            monthly_data_list,
            f"get_cur_total_value_4_mainboard_a error: {err_string}",
        )
    cur_trade_date = tmp_result["date"]
    cur_mainboard_a_value = tmp_result["value"]
    if cur_mainboard_a_value == 0:
        return cur_trade_date, monthly_data_list, f"today is not trade date"

    tmp_result, err_string = query_nationwide_annual_gdp()
    if len(err_string) != 0:
        return (
            cur_trade_date,
            monthly_data_list,
            f"query_nationwide_annual_gdp error: {err_string}",
        )

    for item in tmp_result:
        annual_gdp_data_dict[item.year] = item.gdp

    tmp_result, err_string = query_monthly_total_value_4_mainboard_a()
    if len(err_string) != 0:
        return (
            cur_trade_date,
            monthly_data_list,
            f"query_monthly_total_value_4_mainboard_a error: {err_string}",
        )

    tmp_result.append(
        {
            "date": f"{cur_trade_date[:4]}-{cur_trade_date[4:6]}",
            "value": cur_mainboard_a_value,
        }
    )

    monthly_data_list = []
    for data in tmp_result:
        date_str = data["date"]
        astock = data["value"]
        year, month = date_str.split("-")
        if (int(year) - 1) in annual_gdp_data_dict:
            gdp = annual_gdp_data_dict[int(year) - 1]
        else:
            gdp = annual_gdp_data_dict[int(year) - 2]

        monthly_data_list.append(
            {
                "date": date_str,
                "gdp": gdp,
                "astock": astock,
                "proportion": round(100 * astock / gdp, 2),
            }
        )
    return cur_trade_date, monthly_data_list, ""


def get_avg_interest(symbol, startdate, enddate, region) -> Tuple[float, str]:
    """包含startdate和enddate"""
    interest_df = None
    if region == "cn":
        interest_df = get_stock_interest_yearly_a(symbol)
    elif region == "hk":
        interest_df = get_stock_interest_yearly_hk(symbol)
    elif region == "us":
        interest_df = get_stock_interest_yearly_us(symbol)
    cared_interest_df = interest_df[
        (interest_df["date"] <= enddate) & (interest_df["date"] >= startdate)
    ]
    if len(cared_interest_df) != (enddate.year - startdate.year + 1):
        return 0, f"not enough data for interest"
    return cared_interest_df["value"].mean(), ""


def get_roe_last_n_year(symbol, n=10, region="cn") -> Tuple[str, str]:
    """region cn, hk, us"""
    equity_df = None
    interest_df = None
    if region == "cn":
        equity_df = get_stock_equity_yearly_a(symbol)
        interest_df = get_stock_interest_yearly_a(symbol)
    elif region == "hk":
        equity_df = get_stock_equity_yearly_hk(symbol)
        interest_df = get_stock_interest_yearly_hk(symbol)
    elif region == "us":
        equity_df = get_stock_equity_yearly_us(symbol)
        interest_df = get_stock_interest_yearly_us(symbol)
    if len(equity_df) < n or len(interest_df) < n:
        return "", f"not enough data"
    equity_df = equity_df.sort_values(by=["date"], ascending=False)
    last_ava_data = equity_df.iloc[0]["date"]
    last_equity = equity_df.iloc[0]["value"]
    begin_date_4_equity = datetime.date(
        year=last_ava_data.year - n,
        month=last_ava_data.month,
        day=last_ava_data.day,
    )
    begin_equity = equity_df[equity_df["date"] == begin_date_4_equity].iloc[0]["value"]
    avg_equity = (last_equity + begin_equity) / 2

    avg_interest, err_string = get_avg_interest(
        symbol,
        datetime.date(
            year=last_ava_data.year - n + 1,
            month=last_ava_data.month,
            day=last_ava_data.day,
        ),
        last_ava_data,
        region,
    )
    if len(err_string) != 0:
        return "", err_string
    return f"{round(100*avg_interest/avg_equity, 2)}%", ""


def get_pe_with_avg_interest(symbol, n=5, region="cn") -> Tuple[str, str]:
    """
    仅支持A股 且不支持交易所前缀如sz，sh等
    return pe, err_string
    """
    # 获取当前的市值
    mv_df = None
    if region == "cn":
        mv_df = get_latest_market_value_a(symbol=symbol)
    elif region == "hk":
        mv_df = get_latest_market_value_hk(symbol=symbol)
    elif region == "us":
        mv_df = get_latest_market_value_us(symbol=symbol)
    last_mv_date = mv_df.iloc[0]["date"]
    last_mv_value = mv_df.iloc[0]["value"]
    # 获取avg_interest
    avg_interest, err_string = get_avg_interest(
        symbol,
        datetime.date(year=last_mv_date.year - n, month=1, day=1),
        datetime.date(year=last_mv_date.year - 1, month=12, day=31),
        region,
    )
    if err_string:
        avg_interest, err_string = get_avg_interest(
            symbol,
            datetime.date(year=last_mv_date.year - n - 1, month=1, day=1),
            datetime.date(year=last_mv_date.year - 2, month=12, day=31),
            region,
        )
        if len(err_string) != 0:
            return "0", err_string
    # 计算pe
    return round(last_mv_value / avg_interest, 2), ""


def get_cur_ttm_pe(symbol, region="cn"):
    """
    仅支持A股 且不支持交易所前缀如sz，sh等
    return pe, err_string
    """
    # 获取当前的市值
    mv_df = None
    if region == "cn":
        mv_df = get_latest_ttm_pe_a(symbol=symbol)
    elif region == "hk":
        mv_df = get_latest_ttm_pe_hk(symbol=symbol)
    elif region == "us":
        mv_df = get_latest_ttm_pe_us(symbol=symbol)
    return round(mv_df.iloc[0]["value"], 2)


def get_return_with_today_pe_in_last_n_year(symbol, n=10) -> Tuple[str, str]:
    """
    return return, err_string
    """
    # 获取当前的avg ttm pe
    # 确定过去n年的某个交易日
    #   获取该交易日收盘ttm pe ak.stock_a_indicator_lg
    #   获取该交易日收盘价 ak.stock_zh_a_hist
    #   根据比例计算出当前ttm pe的收盘价
    #   用前复权 or 后复权计算出涨幅 ak.stock_zh_a_hist
    #   根据涨幅和计算出的理论收盘价，计算总体收益率和年化复合收益率
    if not (1 <= n <= 10):
        return 0, "invalid n"
    # 获取过去n年分红总金额
    df1 = None
    pass


def get_avg_interest_metrics():
    """
    TODO
        * 支持美股——Done
        * 看一下苹果和伯克希尔为什么无法获取
        * 支持回看任意历史某一天，然后看看一些历史机会点、风险点的指标特点。
            并总结成使用说明, 即“平均利润指标”的使用说明
        * 支持ROE的趋势
    """
    _cared_stock = json.load(open("conf/cared_stock.json", "r"))
    for s in _cared_stock:
        avg_roe = get_roe_last_n_year(s["symbol"], 5, region=s["region"])
        avg_pe = get_pe_with_avg_interest(s["symbol"], 5, region=s["region"])
        cur_pe = get_cur_ttm_pe(s["symbol"], region=s["region"])
        print(f'{s["name"]} avg_roe: {avg_roe}, avg_pe: {avg_pe}, cur_pe: {cur_pe}')


if __name__ == "__main__":
    get_avg_interest_metrics()

    # print("avg roe", get_roe_last_n_year("09988", 5, region="hk"))
    # print('avg pe', get_pe_with_avg_interest('00883', 5, region='hk'))
    # print('avg pe', get_pe_with_avg_interest('00883', 5))
    # get_astock_status_v2()
