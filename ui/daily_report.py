import pandas as pd
import datetime
from scipy import stats
from biz.daily_report import get_astock_status
from util.data_source.sse import get_last_trading_day_total_value_4_mainboard_a
from util.email import send_html
from util.log import logger

style = '''
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset=utf-8>
</head>
<style>
    body {
        margin-left: 0px;
    }

    .stat_head {font-weight: bold;}
    .stat_detail {padding: 0 24px 2px;}
    .stat_detail_head {font-size: 13px;font-weight: bold;}

    table,table tr th, table tr td { border:1px solid #CDB7B5; font-family: Times, TimesNR, 'New Century Schoolbook',
    Georgia, 'New York', serif;}
    tr {height: 24px;font-size: 15px;}
    td {word-break: keep-all; padding: 0 8px 2px;}
    table {
        width: 100%;
        line-height: 24px;
        text-align: center;
        border-collapse: collapse;
        padding:2px;
    }
    table th {
        font-size: 16px;
        font-weight: bold;
        line-height: 17px;
        padding: 0 8px 2px;
        text-align:center;
        background-color: #DCDCDC;
        position: sticky;
        top: 0;
    }

    .blank {
        z-index: 301;
        background-color: #DCDCDC;
    }

    table tr:nth-child(even){
        background: #f2f2f2;
    }
    tr td:first-child{
        font-size: 13px;
        font-weight: bold;
        line-height: 14px;
        padding: 0 8px 2px;
        text-align:center;
    }
    caption{
        font-size: 150%;
        margin: 10px;
    }
</style>
'''


def daily_report_by_email():
    final_html = ''
    cur_trade_date = ''
    for i in range(1):
        cur_trade_date, monthly_data_list, err_string = get_astock_status()
        if len(err_string) != 0:
            final_html = f'get_astock_status error: {err_string}'
            break

        tmp_cur_date = datetime.datetime.strptime(
            cur_trade_date, '%Y%m%d').date()
        last_trading_day_result, err_string = get_last_trading_day_total_value_4_mainboard_a(
            tmp_cur_date)
        if len(err_string) != 0:
            final_html = f'cur_trading_day={cur_trade_date}||get_last_trading_day_total_value_4_mainboard_a error: {err_string}'
            break
        last_trading_day_astock = last_trading_day_result['value']

        monthly_index_list = [item['date'] for item in monthly_data_list]
        df = pd.DataFrame(monthly_data_list, index=monthly_index_list).sort_index(
            ascending=False)

        # import ipdb
        # ipdb.set_trace()
        result_list = []
        result_index = []
        for i in range(14):
            offset = i*12
            sub_df = df.iloc[(0+offset):(120+offset)
                             ].sort_index(ascending=False)
            cur_record = sub_df.iloc[0]
            cur_proportion = cur_record['proportion']
            cur_quantile = round(stats.percentileofscore(
                sub_df['proportion'], cur_proportion), 2)
            quantile_50 = round(sub_df['proportion'].quantile(0.5), 2)
            quantile_25 = round(sub_df['proportion'].quantile(0.25), 2)
            quantile_75 = round(sub_df['proportion'].quantile(0.75), 2)
            result_index.append(cur_record.name)
            if i == 0:
                last_proportion = round(100 * last_trading_day_astock /
                                        cur_record['gdp'], 2)
                change_rate = round(100 *
                                    (cur_proportion - last_proportion)/last_proportion, 2)
                cur_proportion = f'{cur_proportion}({change_rate}%, {last_proportion})'
            result_list.append((cur_proportion, cur_quantile,
                                quantile_50, quantile_25, quantile_75, round(cur_record['astock']/10000, 2), round(cur_record['gdp']/10000, 2)))

        pd.options.display.float_format = '{:,.2f}'.format
        # import ipdb
        # ipdb.set_trace()
        result_df = pd.DataFrame(result_list, index=result_index, columns=[
            'cur_porportion', 'cur_quantile', 'quantile_50', 'quantile_25', 'quantile_75', 'astock', 'last_gdp'])
        result_df = result_df[['cur_porportion', 'cur_quantile', 'astock', 'last_gdp',
                              'quantile_50', 'quantile_25', 'quantile_75']]
        result_df.rename(columns={
            'cur_porportion': '当前占比',
            'cur_quantile': '过去10年所处分位数',
            'astock': 'A股总市值',
            'last_gdp': '去年GDP',
            'quantile_50': '过去10年50分位值',
            'quantile_25': '过去10年25分位值',
            'quantile_75': '过去10年75分位值',
        },
            inplace=True
        )
        final_html = f'''
        {style}
        {result_df.style.format(precision=2).to_html()}
        '''

    # print(final_html)
    send_html(f'[EDOG]{cur_trade_date}经济报告', final_html)
    logger.info(f'send succeed for {cur_trade_date}')
    return ''


if __name__ == '__main__':
    daily_report_by_email()
