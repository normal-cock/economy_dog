from typing import Tuple, List
import datetime
import pandas as pd
from scipy import stats
from util.data_source.sse import get_cur_total_value_4_mainboard_a, get_last_trading_day_total_value_4_mainboard_a
from util.data_source.zhongjing import query_nationwide_annual_gdp, query_monthly_total_value_4_mainboard_a
from util.email import send_html
from util.log import logger


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
        gdp = annual_gdp_data_dict[int(year)-1]

        monthly_data_list.append({
            'date': date_str,
            'gdp': gdp,
            'astock': astock,
            'proportion': round(100*astock/gdp, 2),
        })
    return cur_trade_date, monthly_data_list, ''
