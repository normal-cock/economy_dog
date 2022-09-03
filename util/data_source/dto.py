from collections import namedtuple


# year:int population:float(万人)
PopulationItem = namedtuple(
    'PopulationItem', ['year', 'population'])
# year:int gdp:float（亿） unit:MONEY_UNIT
GDPItem = namedtuple(
    'GDPItem', ['year', 'gdp', 'unit'])
