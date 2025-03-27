'''
所有指标的标准列: date, value
* date: datetime.date。对于月度聚合数据，取最后一个有数的日子，季度和年度类似
* value: float, 指标的值
* unit: str, 单位
    * None
    * 钱: 万人民币, 亿人民币，万美元，亿美元
    * Pct
'''
import datetime
import pandas as pd
import numpy as np
from metric.stock_data.macro_index.hs300 import hs300_ttm_pe
from metric.stock_data.macro_index.gz import gz_cn_y10, gz_us_y10


def metric_query(
        start_date: datetime.date,
        end_date: datetime.date,
        metric_name: str,
        aggr_type: str = 'euqally',
        final_size=20):
    '''
        指标查询
        * metric_name. hs300_ttm_pe, 
        * start_date. include self
        * end_date. include self
        * aggr_type. equally, monthly, quarterly, yearly
        * final_size. 最终返回的样本量
    '''
    df = None
    if metric_name == 'hs300_ttm_pe':
        df = hs300_ttm_pe()
    elif metric_name == 'gz_cn_y10':
        df = gz_cn_y10(start_date=start_date.strftime('%Y%m%d'))
    elif metric_name == 'gz_us_y10':
        df = gz_us_y10(start_date=start_date.strftime('%Y%m%d'))
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    df = df.dropna()
    df = df.sort_values(by=['date'], ascending=False)
    if aggr_type == 'equally':
        df = _split_into_equal_parts(df, final_size)
    elif aggr_type == 'monthly':
        df = _monthly_avg_aggr(df)
    elif aggr_type == 'quarterly':
        df = _quarterly_avg_aggr(df)
    elif aggr_type == 'yearly':
        df = _yearly_avg_aggr(df)
    df = df.sort_values(by=['date'], ascending=False)
    return df


def _split_into_equal_parts(df, n=10):
    '''
    根据当前顺序将df等分成n份
    '''
    # 使用pd.qcut将df等分成n份
    df['group'] = pd.qcut(np.arange(len(df)), n, labels=False)

    # 对每份进行聚合
    result = df.groupby('group').agg({
        'date': 'max',  # 取每份的最大日期
        'value': 'mean',  # 计算每份的均值
        'unit': 'first'  # 取每份的第一个单位
    }).reset_index(drop=True)

    return result


def _monthly_avg_aggr(df):
    '''
        月度数据，取平均值
    '''
    df['month'] = df.apply((lambda x: x['date'].month), axis=1)
    df['year'] = df.apply((lambda x: x['date'].year), axis=1)
    df = df.groupby(['year', 'month']).agg({
        'date': 'max',
        'value': 'mean',
        'unit': 'first',
    }).reset_index()
    # df['date'] = df.apply(lambda x: _cal_last_day(
    #     x['year'], x['month']), axis=1)
    return df[['date', 'value', 'unit']]


def _quarterly_avg_aggr(df):
    '''
        季度数据，取平均值
    '''
    df['quarter'] = df.apply((lambda x: (
        x['date'].month - 1) // 3 + 1), axis=1)
    df['year'] = df.apply((lambda x: x['date'].year), axis=1)
    df = df.groupby(['year', 'quarter']).agg({
        'date': 'max',
        'value': 'mean',
        'unit': 'first',
    }).reset_index()
    # df['date'] = df.apply(lambda x: _cal_last_day(
    #     x['year'], x['quarter'] * 3), axis=1)
    return df[['date', 'value', 'unit']]


def _yearly_avg_aggr(df):
    '''
        年度数据，取平均值
    '''
    df['year'] = df.apply((lambda x: x['date'].year), axis=1)
    df = df.groupby(['year']).agg({
        'date': 'max',
        'value': 'mean',
        'unit': 'first',
    }).reset_index()
    # df['date'] = df.apply(lambda x: _cal_last_day(
    #     x['year']), axis=1)
    return df[['date', 'value', 'unit']]


def _cal_last_day(year, month=0):
    if month == 0:
        return datetime.date(year, 12, 31)
    # 生成这个月最后一天
    next_month = month + 1
    if next_month == 13:
        next_month = 1
        year += 1
    return datetime.date(year, next_month, 1) - datetime.timedelta(days=1)


if __name__ == '__main__':
    df = metric_query(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 12, 31),
        metric_name='hs300_ttm_pe',
        aggr_type='monthly',
        final_size=12)
    print(df)
