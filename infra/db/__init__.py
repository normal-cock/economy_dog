from datetime import datetime, date
from typing import Tuple, List
from infra.db.model import AnnualPopulation, AnnualGDP, MONEY_UNIT
from init import Session
from model.core import Area, AreaEconomyMetaInfo, AreaEconomyInfo
from sqlalchemy import select

from util.data_source.dto import PopulationItem


def cal_growth_rate(new: float, old: float, duration: int) -> float:
    return round(
        100*(new - old)/old/duration,
        2,
    )


def get_meta_data(
    session: Session,
    area: Area,
) -> AreaEconomyMetaInfo:
    '''
    return
        (changed_time, last_data_year)
    '''
    result = AreaEconomyMetaInfo()
    result.area = area

    gdp_stmt = (
        select(AnnualGDP)
        .where(AnnualGDP.area_code == area.code)
        .order_by(AnnualGDP.year.desc())
    )
    last_gdp_record: AnnualGDP | None = session.scalars(gdp_stmt).first()
    if last_gdp_record == None:
        return result
    population_stmt = (
        select(AnnualPopulation)
        .where(AnnualPopulation.area_code == area.code)
        .order_by(AnnualPopulation.year.desc())
    )
    last_population_record: AnnualPopulation | None = session.scalars(
        population_stmt).first()
    if last_population_record == None:
        return result

    result.changed_time = min(
        last_gdp_record.changed_time, last_population_record.changed_time)
    result.last_data_year = min(
        last_gdp_record.year, last_population_record.year)

    return result


def load_area_economy_info(
    session: Session,
    date: date,
    area: Area,
) -> Tuple[AreaEconomyInfo, str]:
    e_info = AreaEconomyInfo()
    # e_info.area = area
    # e_info.last_data_year = date.year
    year = date.year
    gdp_stmt = (
        select(AnnualGDP)
        .where(AnnualGDP.area_code == area.code)
        .where(AnnualGDP.year.in_(list(range(year-10, year+1))))
        .order_by(AnnualGDP.year.desc())
    )
    # import ipdb
    # ipdb.set_trace()
    gdp_list: List[AnnualGDP] = session.scalars(gdp_stmt).fetchall()
    if len(gdp_list) < 3:
        return e_info, f'area={area}||gdp_list={gdp_list}||not enough record for gdp'
    if gdp_list[0].year != year:
        return e_info, f'area={area}||gdp_list={gdp_list}||no gdp data for {year}'
    population_stmt = (
        select(AnnualPopulation)
        .where(AnnualPopulation.area_code == area.code)
        .where(AnnualPopulation.year.in_(list(range(year-10, year+1))))
        .order_by(AnnualPopulation.year.desc())
    )
    population_list: List[AnnualPopulation] = session.scalars(
        population_stmt).fetchall()
    if len(population_list) < 3:
        return None, f'area={area}||population_list={population_list}||not enough record for population'
    if population_list[0].year != year:
        return e_info, f'area={area}||population_list={population_list}||no population data for {year}'

    e_info.cur_gdp = round(gdp_list[0].number, 2)
    e_info.one_year_gdp = round(gdp_list[1].number, 2)
    e_info.ten_year_gdp = round(gdp_list[-1].number, 2)
    e_info.gdp_unit = gdp_list[0].unit
    e_info.gdp_one_year_growth_rate = cal_growth_rate(
        gdp_list[0].number, gdp_list[1].number, gdp_list[0].year - gdp_list[1].year)
    e_info.gdp_ten_year_growth_rate = cal_growth_rate(
        gdp_list[0].number, gdp_list[-1].number, gdp_list[0].year - gdp_list[-1].year)

    e_info.cur_population = round(population_list[0].number, 2)
    e_info.one_year_population = round(population_list[1].number, 2)
    e_info.ten_year_population = round(population_list[-1].number, 2)
    e_info.population_one_year_growth_rate = cal_growth_rate(
        population_list[0].number,
        population_list[1].number,
        population_list[0].year - population_list[1].year)
    e_info.population_ten_year_growth_rate = cal_growth_rate(
        population_list[0].number,
        population_list[-1].number,
        population_list[0].year - population_list[-1].year)

    cur_gpc = round(gdp_list[0].number / population_list[0].number, 2)
    # gpc_one_year = round(gdp_list[1].number / population_list[1].number, 2)
    # gpc_ten_year = round(gdp_list[-1].number / population_list[-1].number, 2)
    e_info.cur_gdp_per_capita = round(cur_gpc, 2)
    # e_info.one_year_gdp_per_capita = round(gpc_one_year, 2)
    # e_info.ten_year_gdp_per_capita = round(gpc_ten_year, 2)
    # e_info.gpc_one_year_growth_rate = round(
    #     100*(cur_gpc-gpc_one_year)/gpc_one_year, 2)
    # e_info.gpc_ten_year_growth_rate = round(100 *
    #                                         (cur_gpc-gpc_ten_year)/gpc_ten_year/10, 2)

    return e_info, ''
