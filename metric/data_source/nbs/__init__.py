# 国家统计局(national bureau of statistics)
# 代号可以在nbs网站上的网络请求的url中看出来 `https://data.stats.gov.cn/easyquery.htm?cn=C01&zb=A0201&sj=2024`
from typing import Dict, Tuple, List
from util.data_source.dto import GDPItem
from util.log import logger
from cnstats.stats import stats
from model.core import MONEY_UNIT


def query_nationwide_annual_gdp() -> Tuple[List[GDPItem], str]:
    annual_gdp_data_list = stats(
        zbcode='A0201', datestr='2022,2024', dbcode='hgnd')
    result_list = []

    for gdp_data in annual_gdp_data_list:
        if len(gdp_data) != 4 or gdp_data[0] != '国内生产总值':
            logger.warning(f'gdp_data={gdp_data}||invalid gdp_data')
            continue
        result_list.append(GDPItem(
            year=int(gdp_data[2]),
            gdp=float(gdp_data[3]),
            unit=MONEY_UNIT.RMB,
        ))
    return result_list, ''


def query_monthly_total_value_4_mainboard_a() -> Tuple[List[Dict], str]:
    '''股票市价总值，nbs仅有年度该指标, 更新较慢。
    20250318日，还没有2024年的数据。但经过验证，该数据实际是港交所和深交所的每年最后一个交易日的数值相加。
    所以，更新的数据可以通过港交所和深交所来查询。港交所和深交所不支持太老的数据（例如3年前），刚好互补
    zbcode=A0L0C0B
    '''
    return [], ''


if __name__ == "__main__":
    print(query_nationwide_annual_gdp())
