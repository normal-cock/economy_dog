# sse refer to Shanghai Stock Exchange
import json
import requests
import datetime


def get_cur_total_value_4_mainboard_a(target_trade_date=''):
    '''
    主板A+科创板总市值，单位亿元
        target_trade_date格式'2022-10-28'
        return (total_value, err_string)
            total_value为dict {
                'date':'20221028',
                'value':3859.11,
            }
    '''
    callback_name = 'jsonpCallback87201539'
    url = 'http://query.sse.com.cn/commonQuery.do'
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Referer': 'http://www.sse.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }
    params = {
        'jsonCallBack': callback_name,
        'isPagination': 'false',
        'sqlId': 'COMMON_SSE_SJ_SCGM_C',
        'TRADE_DATE': target_trade_date,
    }
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code != 200:
        return 0, f'requests error {resp.status_code} {resp.content}'
    resp_string = resp.text.replace(f'{callback_name}(', '')[:-1]
    resp_dict = json.loads(resp_string)
    zhuban_a = 0
    kechuangban = 0
    trade_date = target_trade_date.replace('-', '')
    for value in resp_dict['result']:
        if value['PRODUCT_NAME'] == '主板A':
            zhuban_a = float(value['TOTAL_VALUE'])
            trade_date = value['TRADE_DATE']
        if value['PRODUCT_NAME'] == '科创板':
            kechuangban = float(value['TOTAL_VALUE'])

    return {
        'date': trade_date,
        'value': zhuban_a+kechuangban,
    }, ''


def get_last_trading_day_total_value_4_mainboard_a(cur_date: datetime.date):
    '''
    return (total_value, err_string)
            total_value为dict {
                'date':'20221028',
                'value':3859.11,
            }
    '''
    total_value = {}
    for i in range(14):
        tmp_date = cur_date - datetime.timedelta(days=i+1)
        tmp_value, err_string = get_cur_total_value_4_mainboard_a(
            tmp_date.strftime('%Y-%m-%d'))
        if len(err_string) != 0:
            return total_value, err_string
        if tmp_value['value'] != 0:
            total_value = tmp_value
            break
    else:
        return total_value, f"can't find last trading day for {cur_date}"
    return total_value, ''


if __name__ == '__main__':
    print(get_cur_total_value_4_mainboard_a())
    print(get_cur_total_value_4_mainboard_a('2022-10-27'))
    cur_date_str = '2022-10-24'
    total_value, err_string = get_cur_total_value_4_mainboard_a(cur_date_str)
    cur_date = datetime.datetime.strptime(total_value['date'], '%Y%m%d').date()
    print(f'last trading day for {cur_date_str} is:',
          get_last_trading_day_total_value_4_mainboard_a(cur_date))
    print(get_cur_total_value_4_mainboard_a('2022-10-23'))
