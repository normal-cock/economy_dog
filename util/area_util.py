import json
from collections import namedtuple
import os
from typing import List, Dict
from util.log import logger
from model.core import Area

_PROVINCE_LIST: List[Area] = []
_CITY_LIST: List[Area] = []
_COUNTY_LIST: List[Area] = []
_CARED_AREA: List[Area] = []

_AREA_NAME_MAP: Dict[str, Area] = {}

_CARED_AREA_NAME = [
    '北京市', '上海市',
    '山西省-太原市', '山西省-临汾市-侯马市', '山西省-临汾市-曲沃县',
    '山西省-运城市-新绛县', '山西省-临汾市', '山西省-运城市',
    '福建省-厦门市',
    '陕西省-西安市',
    '四川省-成都市',
    '江苏省-苏州市-昆山市', '江苏省-无锡市', '江苏省-苏州市', '江苏省-扬州市',
    '宁夏回族自治区-银川市',
    '内蒙古自治区-呼伦贝尔市-满洲里市',
]


def build_area_name_map():
    for area in (_PROVINCE_LIST + _CITY_LIST + _COUNTY_LIST):
        key = area.get_full_name()
        if key in _AREA_NAME_MAP:
            raise Exception(
                f'new_area={area}||old_area={_AREA_NAME_MAP[key]}||duplicated name {key}')
        _AREA_NAME_MAP[key] = area


def load_data():
    province_file = open('util/raw_area_data/province.json')
    for line in province_file:
        line_dict = json.loads(line)
        if ('code' not in line_dict or 'name' not in line_dict or 'url' not in line_dict):
            logger.error('line=%s||invalid line in province.json', line)
        area = Area(
            code=line_dict['code'],
            name=line_dict['name'],
            level=1,
            upper_level_name=line_dict['name'],
            province_name=line_dict['name'],
            url=line_dict['url']
        )
        _PROVINCE_LIST.append(area)
    province_file.close()

    city_file = open('util/raw_area_data/city.json')
    for line in city_file:
        line_dict = json.loads(line)
        if ('code' not in line_dict or 'name' not in line_dict or 'province_name' not in line_dict
                or 'url' not in line_dict):
            logger.error('line=%s||invalid line in city.json', line)
        # 跳过4个直辖市和3个特殊地区
        if line_dict['name'] in ['市辖区', '省直辖县级行政区划', '县', '自治区直辖县级行政区划']:
            continue
        # 被撤销的市
        if line_dict['name'] in ['莱芜市']:
            continue
        # 人口过小的地级市. 三沙市人口不足3000
        if line_dict['name'] in ['三沙市']:
            continue
        # 没有数据的地级市
        if line_dict['name'] in ['巴音郭楞蒙古自治州']:
            continue
        # # 目前没有自治州数据，30个
        # if '自治州' in line_dict['name']:
        #     continue
        area = Area(
            code=line_dict['code'],
            name=line_dict['name'],
            level=2,
            upper_level_name=line_dict['province_name'],
            province_name=line_dict['province_name'],
            url=line_dict['url']
        )
        _CITY_LIST.append(area)
    city_file.close()

    county_file = open('util/raw_area_data/county.json')
    for line in county_file:
        line_dict = json.loads(line)
        if ('code' not in line_dict or 'name' not in line_dict or 'province_name' not in line_dict
                or 'city_name' not in line_dict or 'url' not in line_dict):
            logger.error('line=%s||invalid line in city.json', line)

        # 跳过4个直辖市和3个特殊地区
        if line_dict['name'] in ['市辖区', '省直辖县级行政区划', '县', '自治区直辖县级行政区划']:
            continue

        area = Area(
            code=line_dict['code'],
            name=line_dict['name'],
            level=3,
            upper_level_name=line_dict['city_name'],
            province_name=line_dict['province_name'],
            url=line_dict['url']
        )
        _COUNTY_LIST.append(area)
    county_file.close()

    build_area_name_map()

    for area_name in _CARED_AREA_NAME:
        if area_name not in _AREA_NAME_MAP:
            raise Exception(f'unknown area {area_name}')
        _CARED_AREA.append(_AREA_NAME_MAP[area_name])


load_data()


def get_common_area(level=-1) -> List[Area]:
    if level == 1:
        return _PROVINCE_LIST
    if level == 2:
        return _CITY_LIST

    return _CITY_LIST + _PROVINCE_LIST


def get_cared_area() -> List[Area]:
    return _CARED_AREA


def get_area_need_init() -> List[Area]:
    # return _CARED_AREA + _CITY_LIST + _PROVINCE_LIST
    return _CARED_AREA
    # return _CARED_AREA + _PROVINCE_LIST


if __name__ == '__main__':
    print(len(_PROVINCE_LIST))
    print(len(_CITY_LIST))
    print(len(_CARED_AREA))
