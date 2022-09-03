import enum
import json
from typing import Tuple, List
import re
from bs4 import BeautifulSoup
from util.data_source.parser import year_parser, gdp_unit_parser, population_unit_parser
from util.log import logger
from util.data_source.dto import PopulationItem, GDPItem


class HtmlFormat(enum.Enum):
    SeriesType = 1
    TabDataType = 2
    UnknownType = 999


def parse_format_type(html_string) -> HtmlFormat:
    '''
    return int
    '''
    if 'seriesData' in html_string:
        return HtmlFormat.SeriesType
    elif 'tabData' in html_string:
        return HtmlFormat.TabDataType
    else:
        return HtmlFormat.UnknownType


def validor_and_parser_item_list(html_doc: str) -> Tuple[List, str]:
    '''
        return item_list, err_strin
    '''
    soup = BeautifulSoup(html_doc, 'html.parser')
    atom_list = soup.find_all('script', type="application/json",
                              id=re.compile('atom'))
    if len(atom_list) == 0:
        return [], 'script with atom as id not found'
    data_str = atom_list[0].string
    try:
        data_dict = json.loads(data_str)
    except Exception as e:
        return [], f'data_str={data_str}||invalid json'

    format_type = parse_format_type(html_doc)
    if format_type == HtmlFormat.SeriesType:
        if not ('data' in data_dict and 'tabList' in data_dict['data']):
            return [], f'data_dict={data_dict}||invalid data_dict with no data or tabList field'
        if not (len(data_dict['data']['tabList']) != 0 and
                'chartData' in data_dict['data']['tabList'][0] and
                'seriesData' in data_dict['data']['tabList'][0]['chartData']):
            return [], f'data_dict={data_dict}||invalid data_dict with no chartData or seriesData field'
        if not (len(data_dict['data']['tabList'][0]['chartData']['seriesData']) != 0 and
                'data' in data_dict['data']['tabList'][0]['chartData']['seriesData'][0]):
            return [], f'data_dict={data_dict}||invalid data_dict with no seriesData.data field'
        item_list = data_dict[
            'data']['tabList'][0]['chartData']['seriesData'][0]['data']

        if len(item_list) == 0:
            return [], f'data_dict={data_dict}||empty item_list'

        return item_list, ''
    elif format_type == HtmlFormat.TabDataType:
        if (
            'data' in data_dict and 'tabData' in data_dict['data'] and
            'tabList' in data_dict['data']['tabData'] and
            '年度数据' in data_dict['data']['tabData']['tabList'] and
                'item' in data_dict['data']['tabData']['tabList']['年度数据']):
            item_list = data_dict['data']['tabData']['tabList']['年度数据']['item']
            logger.debug(f"item_list is:{item_list}")

            if len(item_list) == 0:
                return [], f'empty item_list: {data_dict}'
            return item_list, ''
        else:
            return [], f'invalid data_dict: {data_dict}'
    else:
        return [], f'unknown html format'


def parse_gdp_item(item_list) -> Tuple[List[GDPItem], str]:
    result_list = []
    err_str = ''
    for item in item_list:
        if 'text' in item and 'value' in item and 'label' in item:
            tmp_err_str = f'invalid item: {item}'
            year = year_parser(item['label'])
            if year == None:
                err_str = f'item={item}||invalid year'
                break
            try:
                value = float(item['value'])
                times, unit = gdp_unit_parser(item['text'])
            except Exception as e:
                err_str = f'e={e}||{tmp_err_str}'
                break

            result_list.append(GDPItem(
                year=year,
                gdp=value*times,
                unit=unit
            ))
        else:
            err_str = f'item={item}||invalid item'
            break
    if len(err_str) != 0:
        return [], err_str

    return result_list, ''


def parse_populaton_item(item_list) -> Tuple[List[PopulationItem], str]:
    result_list = []
    err_str = ''
    for item in item_list:
        if 'text' in item and 'value' in item and 'label' in item:
            tmp_err_str = f'invalid item: {item}'
            year = year_parser(item['label'])
            if year == None:
                err_str = f'item={item}||invalid year'
                break
            try:
                value = float(item['value'])
                times = population_unit_parser(item['text'])
            except Exception as e:
                err_str = f'e={e}||{tmp_err_str}'
                break

            result_list.append(PopulationItem(
                year=year,
                population=value*times,
            ))
        else:
            err_str = f'item={item}||invalid item'
            break
    if len(err_str) != 0:
        return [], err_str

    return result_list, ''


def parse_gdp_html(html_doc) -> Tuple[List[GDPItem], str]:
    item_list, err_str = validor_and_parser_item_list(html_doc)
    if len(err_str) != 0:
        return '', err_str

    return parse_gdp_item(item_list)


def parse_population_html(html_doc) -> Tuple[List[PopulationItem], str]:
    item_list, err_str = validor_and_parser_item_list(html_doc)
    if len(err_str) != 0:
        return '', err_str

    return parse_populaton_item(item_list)


# def baidu_population_validor(data_dict: dict) -> str:
#     '''
#     return
#         err_str
#     '''

#     if (
#             'data' in data_dict and 'tabData' in data_dict['data'] and
#             'tabList' in data_dict['data']['tabData'] and
#             '年度数据' in data_dict['data']['tabData']['tabList'] and
#             'item' in data_dict['data']['tabData']['tabList']['年度数据']):
#         item_list = data_dict['data']['tabData']['tabList']['年度数据']['item']
#         logger.debug(f"item_list is:{item_list}")
#         if len(item_list) != 0:
#             for item in item_list:
#                 if 'text' in item and 'value' in item and 'label' in item:
#                     err_str = f'invalid item: {item}'
#                     year = year_parser(item['label'])
#                     if year == None:
#                         return f'item={item}||invalid year'
#                     try:
#                         float(item['value'])
#                         population_unit_parser(item['text'])
#                     except Exception as e:
#                         return f'e={e}||{err_str}'
#             return ''
#         return f'empty item_list: {data_dict}'
#     return f'invalid data_dict: {data_dict}'


# def baidu_gdp_validor(data_dict: dict) -> str:
#     '''
#     return
#         err_str
#     '''
#     if (
#             'data' in data_dict and 'tabData' in data_dict['data'] and
#             'tabList' in data_dict['data']['tabData'] and
#             '年度数据' in data_dict['data']['tabData']['tabList'] and
#             'item' in data_dict['data']['tabData']['tabList']['年度数据']):
#         item_list = data_dict['data']['tabData']['tabList']['年度数据']['item']
#         logger.debug(f"item_list is:{item_list}")
#         if len(item_list) != 0:
#             for item in item_list:
#                 if 'text' in item and 'value' in item and 'label' in item:
#                     err_str = f'invalid item: {item}'
#                     year = year_parser(item['label'])
#                     if year == None:
#                         return f'item={item}||invalid year'
#                     try:
#                         float(item['value'])
#                         gdp_unit_parser(item['text'])
#                     except Exception as e:
#                         return f'e={e}||{err_str}'
#             return ''
#         return f'empty item_list: {data_dict}'
#     return f'invalid data_dict: {data_dict}'
