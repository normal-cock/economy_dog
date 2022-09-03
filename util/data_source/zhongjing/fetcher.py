import datetime
import re
import json
import subprocess
import time
import requests
import enum
import urllib
from collections import namedtuple
from typing import Tuple, List
from util.area_util import Area
from util.log import logger
from util.data_source.dto import GDPItem, PopulationItem
from util.data_source.parser import population_unit_parser, gdp_unit_parser

s = requests.Session()
Item = namedtuple("Item", ["id", "unit", "start_time", "end_time"])

_GET_ID_RETRY_TIME = 3


def rebuild_session():
    global s
    s.close()
    s = requests.Session()
    s.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://wap.ceidata.cei.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Cookie': 'userid=26145663-5fd3-4f86-8a59-bba60143a48a; Hm_lvt_f9374eb688ac847bdac045aec2dd6e7c=1660195023; JSESSIONID=F47D8FD75D5399D2B5615D66F8EC0AA1; Hm_lpvt_f9374eb688ac847bdac045aec2dd6e7c=1660810696',
    })


rebuild_session()


_ID_FETCH_URL = "https://wap.ceidata.cei.cn/listSquences"


class QueryDataType(enum.Enum):
    GDP = 1
    PermanentPopulation = 2
    RegisteredPopulation = 3


_INDICATOR_NAME_MAP = {
    QueryDataType.GDP: 'GDP',
    QueryDataType.PermanentPopulation: '常住人口数',
    QueryDataType.RegisteredPopulation: '户籍人口数',
}

_AREA_LEVEL_FILTER = {
    0: {
        'zuzhiid': '3BB7BE25-B805-4ADC-B1F8-8CB3DDFCE93D',
        'zhibiaoid': '3C414365-2C00-4A8A-99E8-E824A01AED42',
        'areaTreeId': '9E27567D-3A30-4641-8231-3440D8D7E7F6',
    },
    1: {
        'zuzhiid': 'DC272815-EB46-4644-9624-CC4850AF56FF',
        'zhibiaoid': '6F7939A3-13CB-4606-8FF2-BC081E92C635',
        'areaTreeId': '2697ADD3-2A26-4564-9D0E-A0A5458E9215',
    },
    2: {
        'zuzhiid': '34396BF3-87CD-47BC-BC4E-7E1E5D553C59',
        'zhibiaoid': '25707F83-CCF5-403A-9D5D-B0E3791DB6B5',
        'areaTreeId': 'D7247CB1-38F0-4874-A30B-D3CCE8868273',
    },
    3: {

        'zuzhiid': '06082D07-E7FB-4D19-A232-49A2294DCA1B',
        'zhibiaoid': '9269FEB4-4E97-430F-9764-C8D07C3FFF0D',
        'areaTreeId': '318D715A-DCC0-45ED-885A-F54FC8CE2AC8',
    },
}


def _get(url, data) -> Tuple[dict, str]:
    try:
        resp = s.post(_ID_FETCH_URL, data=data)
    except Exception as e:
        return {}, f'e={e}||s.post error'
    resp_dict: dict = resp.json()
    return resp_dict, ''


def _get_curl(url, data):
    cmd = f"""curl 'https://wap.ceidata.cei.cn/listSquences'   --data-raw '{urllib.parse.urlencode(data)}'"""
    # print(cmd)
    # output = subprocess.getoutput(cmd)
    output = subprocess.check_output(cmd, shell=True)
    # print(output)
    # import ipdb
    # ipdb.set_trace()
    return json.loads(output)


_AREA_NAME_MAP = {
    '伊犁哈萨克自治州': '伊犁州'
}


def area_name_adaptor(area_name):
    if area_name in _AREA_NAME_MAP:
        return _AREA_NAME_MAP[area_name]
    return area_name


def get_data_item(area: Area, query_data_type: QueryDataType, retry=0) -> Tuple[Item, str]:
    '''
        return Item, err_str
    '''
    err_str = ''
    for i in range(retry+1):
        time.sleep(i*2)
        if i > 0:
            logger.warn(f'previous err_str is {err_str}')
            rebuild_session()
        data = {
            'indicatorCode': '',
            'frequencyCode': '',
            'record': 1,
            'pageIndex': 1,
        }
        data.update(_AREA_LEVEL_FILTER[area.level])
        condition = f'{area_name_adaptor(area.name)} {_INDICATOR_NAME_MAP[query_data_type]}'
        data['condition'] = condition
        logger.debug(
            f'condition={condition}||type={query_data_type}||data={data}||get_data_item request data')
        resp_dict, err_str = _get(_ID_FETCH_URL, data)
        if len(err_str) != 0:
            continue
        if 'errcode' not in resp_dict or resp_dict['errcode'] != 100:
            err_str = f"condition={condition}||type={query_data_type}||errcode={resp_dict.get('errcode')}||errmsg={resp_dict.get('errmsg')}||resp content error"
            continue
        if 'sequenceInfo' not in resp_dict or len(resp_dict['sequenceInfo']) == 0:
            err_str = f'condition={condition}||type={query_data_type}||content={resp_dict}||invalid content format'
            continue
        related_item_list = []
        for item in resp_dict['sequenceInfo']:
            if '【停】' in item['areaName']:
                err_str = f'condition={condition}||type={query_data_type}||area={area}||area status changed'
                logger.warn(err_str)
                break
            if (item['indicatorName'] == _INDICATOR_NAME_MAP[query_data_type] and
                    item['areaName'].strip('州省') in area.name and
                    item['areaName'][0] == area.name[0]):
                related_item_list.append(item)
        logger.debug(
            f'condition={condition}||type={query_data_type}||len={len(related_item_list)}||related_item_list len')
        if len(related_item_list) != 1:
            err_str = f'condition={condition}||type={query_data_type}||related_item_list={related_item_list}||related_item_list len error'
            break
        err_str = ''
        break

    if len(err_str) != 0:
        return '', f'{err_str} after retry {retry} times'
    if i > 0:
        logger.info(f'succeed after {i} retry')

    return Item(
        id=related_item_list[0]['id'],
        unit=related_item_list[0]['unit'],
        start_time=datetime.datetime.strptime(
            related_item_list[0]['startTime'], "%Y-%m-%d %H:%M:%S"),
        end_time=datetime.datetime.strptime(
            related_item_list[0]['endTime'], "%Y-%m-%d %H:%M:%S"),
    ), ''


def query_gdp(area: Area) -> Tuple[List[GDPItem], str]:
    result_list = []
    item, err_str = get_data_item(area, QueryDataType.GDP, _GET_ID_RETRY_TIME)
    if len(err_str) != 0:
        return result_list, err_str
    times, unit = gdp_unit_parser(item.unit)
    resp = requests.get('https://wap.ceidata.cei.cn/detail', params={
        'id': item.id,
    })
    if resp.status_code != 200:
        return result_list, f'status_code={resp.status_code}||get detail error'

    re_result = re.search("var chartData = JSON.parse\(\'(.*)\'\);", resp.text)
    if re_result == None:
        return result_list, f'content={resp.text}||invalid detail response'
    if len(re_result.groups()) != 1:
        return result_list, f'groups={re_result.groups()}||invalid detail response'
    for chart_data in eval(re_result.groups()[0]):
        if 'innerTime' not in chart_data or 'data' not in chart_data:
            logger.warn(f'chart_data={chart_data}||invalid chart_data')
            continue
        result_list.append(GDPItem(
            year=int(chart_data['innerTime']),
            gdp=float(chart_data['data']) * times,
            unit=unit,
        ))
    return result_list, ''


def query_population(area: Area) -> Tuple[List[PopulationItem], str]:
    # import ipdb
    # ipdb.set_trace()
    result_list = []
    item, err_str = get_data_item(
        area, QueryDataType.PermanentPopulation, _GET_ID_RETRY_TIME)
    if len(err_str) != 0:
        return result_list, err_str
    # 对于常住人口数的统计时间范围小于5年的，用“户籍人口数”
    if (item.end_time - item.start_time).days/365 < 5:
        logger.info(
            f'area={area}||PermanentPopulation is not enough, try to use registered population')
        item, err_str = get_data_item(
            area, QueryDataType.RegisteredPopulation, _GET_ID_RETRY_TIME)
        if len(err_str) != 0:
            return result_list, err_str
    times = population_unit_parser(item.unit)
    resp = requests.get('https://wap.ceidata.cei.cn/detail', params={
        'id': item.id,
    })
    if resp.status_code != 200:
        return result_list, f'status_code={resp.status_code}||get detail error'

    re_result = re.search("var chartData = JSON.parse\(\'(.*)\'\);", resp.text)
    if re_result == None:
        return result_list, f'content={resp.text}||invalid detail response'
    if len(re_result.groups()) != 1:
        return result_list, f'groups={re_result.groups()}||invalid detail response'
    for chart_data in eval(re_result.groups()[0]):
        if 'innerTime' not in chart_data or 'data' not in chart_data:
            logger.warn(f'chart_data={chart_data}||invalid chart_data')
            continue
        result_list.append(PopulationItem(
            year=int(chart_data['innerTime']),
            population=float(chart_data['data']) * times,
        ))
    return result_list, ''


def self_check():
    from util.area_util import get_area_need_init, Area
    area_list = get_area_need_init()
    # area_list = [
    #     Area(**{'code': '210600000000', 'name': '丹东市', 'level': 2, 'province_name': '辽宁省',
    #             'url': 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/2106.html'}),
    #     Area(**{'code': '210500000000', 'name': '本溪市', 'level': 2, 'province_name': '辽宁省',
    #          'url': 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/2105.html'}),
    # ]
    # begin_index = 165 + 60 + 100
    begin_index = 0
    area_list = area_list[begin_index:100]
    total_number = len(area_list)
    fail_number = 0
    retry_time = 3
    for i, area in enumerate(area_list):
        id_str, err_str = get_data_item(
            area, QueryDataType.GDP, retry=retry_time)
        if len(err_str) != 0:
            logger.error(
                f'area={area}||err_str={err_str}')
            fail_number += 1
            # time.sleep(30)
            continue
        id_str, err_str = get_data_item(
            area, QueryDataType.PermanentPopulation, retry=retry_time)
        if len(err_str) != 0:
            logger.error(
                f'area={area}||err_str={err_str}')
            fail_number += 1
            # time.sleep(30)
            continue
        logger.info(
            f'{area.get_full_name()} succeed. progress {i+1}/{total_number}')
        # time.sleep(1)


if __name__ == '__main__':
    # self_check()
    area = Area(
        code='141081000000',
        name='侯马市',
        level=3,
        upper_level_name='临汾市',
        province_name='山西省',
        url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/10/141081.html',
    )
    # area = Area(
    #     code='11',
    #     name='北京市',
    #     level=1,
    # upper_level_name = '北京市',
    #     province_name='北京市',
    #     url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/10/141081.html',
    # )
    print(query_gdp(area))
    print(query_population(area))
    # print(f'{area.get_full_name()} GDP id: ',
    #         get_data_item(area, QueryDataType.GDP))
    # print(f'{area.get_full_name()} Population id: ',
    #         get_data_item(area, QueryDataType.Population))
