from collections import namedtuple


PopulationItem = namedtuple(
    'PopulationItem', ['year', 'population'])
'''year:int population:float(万人)'''

GDPItem = namedtuple(
    'GDPItem', ['year', 'gdp', 'unit'])
'''ear:int gdp:float（亿） unit:MONEY_UNIT'''
