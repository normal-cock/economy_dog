from datetime import date
from typing import List, Tuple
from init import Session
import pandas as pd
from model.core import Area, AreaEconomyInfo, AreaEconomyMetaInfo
from util.area_util import get_cared_area, get_common_area
from infra.db import get_meta_data, load_area_economy_info
from util.log import logger
from biz.download_data import download_and_save_one_area


class AnnualReportDTO(object):
    common_df: pd.DataFrame

    population_one_year_growth_rate_top10: List[AreaEconomyInfo]
    population_one_year_growth_rate_last10: List[AreaEconomyInfo]
    population_ten_year_growth_rate_top10: List[AreaEconomyInfo]
    population_ten_year_growth_rate_last10: List[AreaEconomyInfo]
    population_top_list: List[AreaEconomyInfo]
    population_last_list: List[AreaEconomyInfo]

    gdp_one_year_growth_rate_top10: List[AreaEconomyInfo]
    gdp_one_year_growth_rate_last10: List[AreaEconomyInfo]
    gdp_ten_year_growth_rate_top10: List[AreaEconomyInfo]
    gdp_ten_year_growth_rate_last10: List[AreaEconomyInfo]
    gdp_top_list: List[AreaEconomyInfo]
    gdp_last_list: List[AreaEconomyInfo]
    gpc_top_list: List[AreaEconomyInfo]
    gpc_last_list: List[AreaEconomyInfo]

    cared_area: List[AreaEconomyInfo]

    high_quality_area: List[AreaEconomyInfo]

    err_area_list: List[Tuple[Area, str]]


_TOP_NUMBER = 20


def _load_or_download_e_info(
    session: Session,
    area: Area,
    target_date: date
) -> Tuple[AreaEconomyInfo, str]:
    err_str = ''
    tmp_date = target_date
    e_meta_info = get_meta_data(session, area)
    need_redownload = e_meta_info.need_redownload(tmp_date)
    if need_redownload:
        err_str = download_and_save_one_area(session, area)
        if len(err_str) != 0:
            err_str = f'err_str={err_str}||area={area}||error when download_and_save_one_area'
            return None, err_str

    e_info, err_str = load_area_economy_info(session, tmp_date, area)
    if len(err_str) != 0:
        tmp_date = tmp_date.replace(year=tmp_date.year-1)
        e_info, err_str = load_area_economy_info(session, tmp_date, area)
        if len(err_str) != 0:
            err_str = f'err_str={err_str}||area={area}||error when load economy_info'
            return None, err_str
    e_info.meta_data = e_meta_info
    return e_info, err_str


def _fetch_high_quality_area_elist(common_df: pd.DataFrame) -> List[AreaEconomyInfo]:
    population_one_year_growth_rate_threshold = common_df['population_one_year_growth_rate'].quantile(
        0.75)
    population_ten_year_growth_rate_threshold = common_df['population_ten_year_growth_rate'].quantile(
        0.75)
    gdp_one_year_growth_rate_threshold = common_df['gdp_one_year_growth_rate'].quantile(
        0.50)
    gdp_ten_year_growth_rate_threshold = common_df['gdp_ten_year_growth_rate'].quantile(
        0.50)
    cur_gdp_per_capita_threshold = common_df['cur_gdp_per_capita'].quantile(
        0.50)

    high_quality_df = (common_df[common_df['population_one_year_growth_rate']
                                 >= population_one_year_growth_rate_threshold]
                       [common_df['population_ten_year_growth_rate']
                           >= population_ten_year_growth_rate_threshold]
                       [common_df['gdp_one_year_growth_rate']
                           >= gdp_one_year_growth_rate_threshold]
                       [common_df['gdp_ten_year_growth_rate']
                           >= gdp_ten_year_growth_rate_threshold]
                       )
    return list(high_quality_df['e_info'])


def annual_report_result(cur_date: date) -> AnnualReportDTO:
    dto = AnnualReportDTO()
    session = Session()
    common_list = []
    cared_list = []
    err_area_list = []

    for area in get_common_area():
        e_info, err_str = _load_or_download_e_info(session, area, cur_date)
        if len(err_str) != 0:
            logger.error(err_str)
            err_area_list.append((area, err_str))
            continue
        tmp_dict = e_info.gen_dict()
        tmp_dict.update({'e_info': e_info})
        logger.debug(f'{area.get_full_name()} is added')
        common_list.append(tmp_dict)
    common_df = pd.DataFrame(common_list)
    # import ipdb
    # ipdb.set_trace()
    common_df = common_df[common_df['cur_population'] > 500]
    dto.common_df = common_df

    dto.population_one_year_growth_rate_top10 = list(common_df.nlargest(
        _TOP_NUMBER, 'population_one_year_growth_rate')['e_info'])
    dto.population_one_year_growth_rate_last10 = list(common_df.nsmallest(
        _TOP_NUMBER, 'population_one_year_growth_rate')['e_info'])
    dto.population_ten_year_growth_rate_top10 = list(common_df.nlargest(
        _TOP_NUMBER, 'population_ten_year_growth_rate')['e_info'])
    dto.population_ten_year_growth_rate_last10 = list(common_df.nsmallest(
        _TOP_NUMBER, 'population_ten_year_growth_rate')['e_info'])
    dto.population_top_list = list(common_df.nlargest(
        _TOP_NUMBER, 'cur_population')['e_info'])
    dto.population_last_list = list(common_df.nsmallest(
        _TOP_NUMBER, 'cur_population')['e_info'])

    dto.gdp_one_year_growth_rate_top10 = list(common_df.nlargest(
        _TOP_NUMBER, 'gdp_one_year_growth_rate')['e_info'])
    dto.gdp_one_year_growth_rate_last10 = list(common_df.nsmallest(
        _TOP_NUMBER, 'gdp_one_year_growth_rate')['e_info'])
    dto.gdp_ten_year_growth_rate_top10 = list(common_df.nlargest(
        _TOP_NUMBER, 'gdp_ten_year_growth_rate')['e_info'])
    dto.gdp_ten_year_growth_rate_last10 = list(common_df.nsmallest(
        _TOP_NUMBER, 'gdp_ten_year_growth_rate')['e_info'])
    dto.gdp_top_list = list(common_df.nlargest(
        _TOP_NUMBER, 'cur_gdp')['e_info'])
    dto.gdp_last_list = list(common_df.nsmallest(
        _TOP_NUMBER, 'cur_gdp')['e_info'])
    dto.gpc_top_list = list(common_df.nlargest(
        _TOP_NUMBER, 'cur_gdp_per_capita')['e_info'])
    dto.gpc_last_list = list(common_df.nsmallest(
        _TOP_NUMBER, 'cur_gdp_per_capita')['e_info'])

    for area in get_cared_area():
        e_info, err_str = _load_or_download_e_info(session, area, cur_date)
        if len(err_str) != 0:
            logger.error(err_str)
            err_area_list.append((area, err_str))
            continue

        cared_list.append(e_info)

    dto.cared_area = cared_list
    dto.high_quality_area = _fetch_high_quality_area_elist(common_df)

    dto.err_area_list = err_area_list
    return dto


if __name__ == '__main__':
    print(annual_report_result().__dict__)
