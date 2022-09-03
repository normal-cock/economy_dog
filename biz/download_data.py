import time
from model.core import Area
from util.area_util import get_area_need_init
from util.data_source import query_gdp, query_population
from init import Session
from util.log import logger
from infra.db import AnnualGDP, AnnualPopulation, MONEY_UNIT


def download_data(year):
    pass


def download_and_save_one_area(session: Session, area: Area) -> str:
    '''
    return
        err_str
    '''
    logger.info(f'try to download data for {area}')
    result_list, err_str = query_population(area)
    if len(err_str) != 0:
        return f'err_str={err_str}||query_population error'
    for result in result_list:
        session.add(AnnualPopulation(
            area_code=area.code,
            year=result.year,
            number=result.population,
        ))

    session.commit()

    logger.info(
        f'upserted={len(result_list)}||area={area}||finished download population data for {area.get_full_name()}')

    result_list, err_str = query_gdp(area)
    if len(err_str) != 0:
        return f'err_str={err_str}||query_gdp error'
    for result in result_list:
        session.add(AnnualGDP(
            area_code=area.code,
            year=result.year,
            number=result.gdp,
            unit=result.unit,
        ))

    session.commit()

    logger.info(
        f'upserted={len(result_list)}||area={area}||finished download population data for {area.get_full_name()}')

    return ''


def download_init_area_data():
    logger.info('download_init_area_data begin')
    session = Session()
    area_list = set(get_area_need_init())
    err_area_list = set()

    # download population data
    for i, area in enumerate(area_list):
        logger.info(
            f'begin download population data for {area.get_full_name()} (progress:{i+1}/{len(area_list)})')
        err_str = download_and_save_one_area(session, area)
        if len(err_str) != 0:
            logger.error(f'err_str={err_str}||download_one_area error')
            err_area_list.add(area)
            continue

    logger.info(
        f'success_area={len(area_list-err_area_list)}||fail_ares={len(err_area_list)}||fail_ares={err_area_list}||download_init_area_data ended')

    session.close()
