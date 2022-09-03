import enum
import datetime
from sqlalchemy import Column, Float, Enum, Integer, String, DateTime, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from model import MONEY_UNIT

Base = declarative_base()


class AnnualPopulation(Base):
    __tablename__ = 'annual_population'
    id = Column(Integer, primary_key=True)
    area_code = Column(String(64), index=True, nullable=True)
    year = Column(Integer, nullable=True)
    # 单位为万人
    number = Column(Float, default=0)

    created_time = Column(DateTime, default=datetime.datetime.now)
    changed_time = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # 关于upsert: https://stackoverflow.com/questions/7165998/how-to-do-an-upsert-with-sqlalchemy
    # sqlite_on_conflict需要手动在alembic生成的versions中修改
    __table_args__ = (UniqueConstraint(
        'year', 'area_code', sqlite_on_conflict='REPLACE'),)


class AnnualGDP(Base):
    __tablename__ = 'annual_gdp'
    id = Column(Integer, primary_key=True)
    area_code = Column(String(64), index=True, nullable=True)
    year = Column(Integer, nullable=True)
    # 单位为亿
    number = Column(Float, default=0)
    unit = Column(Enum(MONEY_UNIT), nullable=True)

    created_time = Column(DateTime, default=datetime.datetime.now)
    changed_time = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    __table_args__ = (UniqueConstraint(
        'year', 'area_code', sqlite_on_conflict='REPLACE'),)
