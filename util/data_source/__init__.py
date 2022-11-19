import json
from typing import Tuple, List
from util.data_source.dto import GDPItem, PopulationItem
# from util.data_source import baidu
from util.data_source import zhongjing
from util.area_util import Area
from util.log import logger


def query_gdp(area: Area) -> Tuple[List[GDPItem], str]:
    '''
    return gdp_list, err_str
        其中gdp_list格式为[util.data_source.validator.GDPItem]
    '''
    # return baidu.query_gdp(area)
    return zhongjing.query_gdp(area)


def query_population(area: Area) -> Tuple[List[PopulationItem], str]:
    '''
    return population_list, err_str
        其中population_list格式为[util.data_source.validator.PopulationItem]，人口单位为万
    '''
    # return baidu.query_population(area)
    return zhongjing.query_population(area)


if __name__ == '__main__':
    # result_list, err_str = query_population('侯马')
    # print(result_list, err_str)
    area = Area(
        code='141081000000',
        name='侯马市',
        level=3,
        upper_level_name='临汾市',
        province_name='山西省',
        url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/10/141081.html',
    )
    result_list, err_str = query_gdp(area)
    print(result_list, err_str)
