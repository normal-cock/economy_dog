import datetime
from akshare import stock_index_pe_lg, bond_zh_us_rate, stock_hk_gxl_lg
import pandas as pd


def gz_cn_y10(start_date: str = "19901219"):
    df = bond_zh_us_rate(start_date)
    df['date'] = df['日期']
    df['value'] = df['中国国债收益率10年']
    df['unit'] = "None"
    df = df[['date', 'value', 'unit']]
    return df


def gz_us_y10(start_date: str = "19901219"):
    df = bond_zh_us_rate(start_date)
    df['date'] = df['日期']
    df['value'] = df['美国国债收益率10年']
    df['unit'] = "None"
    df = df[['date', 'value', 'unit']]
    return df


if __name__ == '__main__':
    print(bond_zh_us_rate('19920101'))
    # with pd.option_context('display.max_columns', None):
