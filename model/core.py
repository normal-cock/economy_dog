from datetime import datetime, date
import enum


class MONEY_UNIT(enum.Enum):
    RMB = 1
    DOLLAR = 2


class Area(object):
    code: str
    name: str
    # 国家为0, 省的level为1，地级市的level为2，县级市(country)为3
    level: int
    upper_level_name: str
    province_name: str
    url: str

    def __init__(self, code, name, level, upper_level_name, province_name, url) -> None:
        self.code = code
        self.name = name
        self.level = level
        self.upper_level_name = upper_level_name
        self.province_name = province_name
        self.url = url

    def get_full_name(self) -> str:
        full_area_name = self.name
        if self.level == 2:
            full_area_name = f'{self.province_name}-{self.name}'
        if self.level == 3:
            full_area_name = f'{self.province_name}-{self.upper_level_name}-{self.name}'
        return full_area_name

    def __str__(self):
        return f'{self.__dict__}'

    def __repr__(self) -> str:
        return f'{self.__dict__}'


class AreaEconomyMetaInfo(object):
    area: Area
    last_data_year: int
    # 所有记录中最早的changed_time
    changed_time: datetime

    def __init__(self):
        self.area = None
        self.last_data_year = 0
        self.changed_time = None

    def need_redownload(self, target_last_date: date) -> bool:
        if self.changed_time == None or self.last_data_year == 0:
            return True

        if target_last_date.year <= self.last_data_year:
            return False
        else:
            update_delta = datetime.now() - self.changed_time
            if update_delta.days > 30:
                return True
            else:
                return False

    def __str__(self):
        return f'{self.__dict__}'

    def __repr__(self) -> str:
        return f'{self.__dict__}'


class AreaEconomyInfo(object):
    '''
    rate的单位都是0.01，且都是一年，例如ten_year_growth_rate为10年增长率除以10
    '''
    meta_data: AreaEconomyMetaInfo
    # 单位亿
    cur_gdp: float
    one_year_gdp: float
    ten_year_gdp: float
    gdp_unit: MONEY_UNIT

    gdp_one_year_growth_rate: float
    gdp_ten_year_growth_rate: float

    # 单位万人
    cur_population: float
    one_year_population: float
    ten_year_population: float
    # rate的单位都是0.01
    population_one_year_growth_rate: float
    population_ten_year_growth_rate: float

    # 单位万
    cur_gdp_per_capita: float
    one_year_gdp_per_capita: float
    ten_year_gdp_per_capita: float
    # rate的单位都是0.01
    gpc_one_year_growth_rate: float
    gpc_ten_year_growth_rate: float

    def gen_dict(self) -> dict:
        tmp_dict: dict = {}
        tmp_dict.update(self.__dict__)
        tmp_dict.pop('meta_data')
        tmp_dict.update(self.meta_data.__dict__)
        area = self.meta_data.area
        tmp_dict['area'] = f'{area.get_full_name()}({area.code})'
        return tmp_dict

    def __str__(self):
        return f'{self.__dict__}'

    def __repr__(self) -> str:
        return f'{self.__dict__}'
