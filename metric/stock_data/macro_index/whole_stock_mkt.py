from akshare import stock_index_pe_lg, bond_zh_us_rate, stock_hk_gxl_lg
import pandas as pd


def monthly_pe_4_hs300():
    print(stock_index_pe_lg(symbol="沪深300"))


if __name__ == '__main__':
    monthly_pe_4_hs300()
    with pd.option_context('display.max_columns', None):
        print(bond_zh_us_rate())
