import akshare as ak
from util.stock_data.etf_info import query_etf_symbol
from util.log import logger

_LOW_VOLUME_THRESHOLD = 0.8
# _LOW_VOLUME_THRESHOLD = 1


def need_notice(etf_names):
    '''
        return result_dict, err_result_dict
    '''
    result_dict = {}
    err_result_dict = {}
    for etf_name in etf_names:
        is_need_notice, err_string = _need_notice(etf_name=etf_name)
        if len(err_string) != 0:
            err_result_dict[etf_name] = err_string
        result_dict[etf_name] = is_need_notice

    return result_dict, err_result_dict


def _need_notice(etf_name):
    '''
        whehter encourtered two successive low volume increase in recent 7 days
            low volumn: volumn<_LOW_VOLUME_THRESHOLD * mean_volume_50d
        return (bool, err_string)
    '''
    is_need_notice = False
    etf_symbol = query_etf_symbol(etf_name)
    if etf_symbol == None:
        return is_need_notice, f"{etf_name} not found"
    df = ak.fund_etf_hist_sina(symbol=etf_symbol)
    if len(df) < 60:
        return is_need_notice, f"{etf_name} don't have enough data (len={len(df)})"

    tmp_counter = 0
    df = df.sort_values(by=['date'], ascending=False)

    for i in range(7):
        volume_50d = df.iloc[i:i+50]['volume']
        mean_volume_50d = volume_50d.mean()
        row = df.iloc[i]
        is_increase = row['close'] >= row['open']
        is_low_volume = row['volume'] < (
            _LOW_VOLUME_THRESHOLD * mean_volume_50d)
        logger.info(
            f"{etf_name}\t{row['date']}"
            f"\t{'Red' if is_increase else 'green'}"
            f"\tis_low_volume={is_low_volume}")
        if is_increase:
            if is_low_volume:
                tmp_counter += 1
            else:
                tmp_counter = 0
        if tmp_counter >= 2:
            break
    if tmp_counter >= 2:
        return True, ''
    return False, ''


if __name__ == '__main__':
    # print(need_notice(['新能源ETF', '大数据ETF', '酒ETF', '芯片ETF', '上证指数ETF']))
    print(need_notice(['酒ETF']))
