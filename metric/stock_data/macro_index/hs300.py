import datetime
from akshare import stock_index_pe_lg, bond_zh_us_rate, stock_hk_gxl_lg
import pandas as pd


def hs300_ttm_pe():
    '''滚动市盈率'''
    df = stock_index_pe_lg(symbol="沪深300")
    df['date'] = df['日期']
    df['value'] = df['滚动市盈率']
    df['unit'] = "None"
    df = df[['date', 'value', 'unit']]
    return df


if __name__ == '__main__':
    hs300_ttm_pe()
    with pd.option_context('display.max_columns', None):
        print(bond_zh_us_rate())
