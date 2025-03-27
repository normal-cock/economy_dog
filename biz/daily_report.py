from typing import Tuple, List
import datetime
import pandas as pd
import plotly.express as px
from scipy import stats
from jinja2 import Environment, FileSystemLoader
from metric.data_source.sse import get_cur_total_value_4_mainboard_a, get_last_trading_day_total_value_4_mainboard_a
from metric.data_source.zhongjing import query_nationwide_annual_gdp, query_monthly_total_value_4_mainboard_a
from metric import metric_query
from util.email import send_html
from util.log import logger

_CARED_ETF = ['']
jinja_env = Environment(loader=FileSystemLoader('template'))
daily_report_tpl = jinja_env.get_template('daily_report.html')


def _gen_trend_html(df, cur_value):
    std_pct = [0.25, 0.5, 0.75]
    std_pct_value = df['value'].quantile(std_pct)
    fig = px.line(
        x=df['date'],
        y=df['value'],)

    for i, pct_value in enumerate(std_pct_value):
        rounded_pct_value = round(pct_value, 2)
        fig.add_hline(
            y=rounded_pct_value,
            line_dash="dash",
            line_color="red",
            line_width=0.8,
            annotation_text=f"{rounded_pct_value} ({int(std_pct[i]*100)}th)", annotation_position="top right")

    fig.update_layout(
        xaxis_title=None,  # 隐藏 X 轴标签
        yaxis_title=None,  # 隐藏 Y 轴标签
        width=400,
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),  # 调整边距
        hovermode="x unified")
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def _gen_column_one_metric(metric_name):
    today = datetime.date.today()
    cur_df = metric_query(
        metric_name=metric_name,
        start_date=today-datetime.timedelta(days=10),
        end_date=today,
    )
    cur_value = cur_df['value'].iloc[0]
    cur_date = cur_df['date'].iloc[0]
    cur_value_html = f'{cur_value} ({cur_date})'

    y10_monthly_df = metric_query(
        metric_name=metric_name,
        start_date=datetime.date(today.year-10, 1, 1),
        end_date=today,
        aggr_type='quarterly',
    )
    y10_quantile = round(stats.percentileofscore(
        y10_monthly_df['value'], cur_value), 2)

    y10_quantile_html = f'{y10_quantile}th'
    y10_trend_html = _gen_trend_html(y10_monthly_df, cur_value)

    y50_yearly_df = metric_query(
        metric_name=metric_name,
        start_date=datetime.date(today.year-50, 1, 1),
        end_date=today,
        aggr_type='yearly',
    )
    print(y50_yearly_df)
    y50_quantile = round(stats.percentileofscore(
        y50_yearly_df['value'], cur_value), 2)

    y50_quantile_html = f'{y50_quantile}th'
    y50_trend_html = _gen_trend_html(y50_yearly_df, cur_value)

    return (
        cur_value_html,
        y10_quantile_html,
        y10_trend_html,
        y50_quantile_html,
        y50_trend_html)


def get_astock_status_v2() -> str:
    '''返回值为html'''
    metrics = {
        "hs300_ttm_pe": "沪深300动态市盈率",
        "gz_cn_y10": "中国10年国债收益率",
        "gz_us_y10": "美国10年国债收益率",
    }
    metric_results = []
    for metric_key, metric_name in metrics.items():
        html_result = _gen_column_one_metric(metric_key)
        metric_results.append([metric_name, *html_result])

    rendered_html = daily_report_tpl.render(
        metrics=metric_results
    )
    print(rendered_html)


def get_astock_status() -> Tuple[str, List, str]:
    '''
        return cur_trade_date, monthly_data_list, err_string
        list元素为{
            'date' # 日期，2022-10
            'gdp' # 去年gdp
            'astock' # 当月A股总市值
            'proportion' # round(100*astock/gdp, 2)
        }
    '''
    monthly_data_list = []
    cur_trade_date = ''
    cur_mainboard_a_value = 0
    annual_gdp_data_dict = {}
    tmp_result, err_string = get_cur_total_value_4_mainboard_a()
    if len(err_string) != 0:
        return cur_trade_date, monthly_data_list, f'get_cur_total_value_4_mainboard_a error: {err_string}'
    cur_trade_date = tmp_result['date']
    cur_mainboard_a_value = tmp_result['value']
    if cur_mainboard_a_value == 0:
        return cur_trade_date, monthly_data_list, f'today is not trade date'

    tmp_result, err_string = query_nationwide_annual_gdp()
    if len(err_string) != 0:
        return cur_trade_date, monthly_data_list, f'query_nationwide_annual_gdp error: {err_string}'

    for item in tmp_result:
        annual_gdp_data_dict[item.year] = item.gdp

    tmp_result, err_string = query_monthly_total_value_4_mainboard_a()
    if len(err_string) != 0:
        return cur_trade_date, monthly_data_list, f'query_monthly_total_value_4_mainboard_a error: {err_string}'

    tmp_result.append({
        'date': f'{cur_trade_date[:4]}-{cur_trade_date[4:6]}',
        'value': cur_mainboard_a_value,
    })

    monthly_data_list = []
    for data in tmp_result:
        date_str = data['date']
        astock = data['value']
        year, month = date_str.split('-')
        if (int(year)-1) in annual_gdp_data_dict:
            gdp = annual_gdp_data_dict[int(year)-1]
        else:
            gdp = annual_gdp_data_dict[int(year)-2]

        monthly_data_list.append({
            'date': date_str,
            'gdp': gdp,
            'astock': astock,
            'proportion': round(100*astock/gdp, 2),
        })
    return cur_trade_date, monthly_data_list, ''


if __name__ == '__main__':
    get_astock_status_v2()
