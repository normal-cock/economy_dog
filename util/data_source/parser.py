import re
import enum
from typing import Tuple

from model.core import MONEY_UNIT


def year_parser(input):
    result = re.match('^([12]{1}[0-9]{3})年$', input)
    if result == None:
        return result
    return result.groups()[0]


def population_unit_parser(input) -> float:
    '''返回要换算成万的话要乘的倍数'''
    if '亿' in input:
        return 10000
    elif '万' in input:
        return 1
    elif '人' in input:
        return float(1)/10000
    else:
        raise Exception(f'unknow population unit {input}')


def gdp_unit_parser(input) -> Tuple[float, MONEY_UNIT]:
    '''
    return times, unit
        times: 要换算成亿的话要乘的倍数
        unit: 1为RMB, 2为美元
    '''
    if '万亿元' in input:
        return 10000, MONEY_UNIT.RMB
    elif '亿元' in input:
        return 1, MONEY_UNIT.RMB
    elif '万元' in input:
        return float(1)/10000, MONEY_UNIT.RMB
    elif '万亿美元' in input:
        return 10000, MONEY_UNIT.DOLLAR
    elif '亿美元' in input:
        return 1, MONEY_UNIT.DOLLAR
    else:
        raise Exception(f'unknow GDP unit {input}')
