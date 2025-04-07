# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, SmallInteger, String, Text, Time

from xivo_dao.helpers.db_manager import Base


class StatsConf(Base):
    __tablename__ = 'stats_conf'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('stats_conf__idx__disable', 'disable'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, server_default='')
    hour_start = Column(Time, nullable=False)
    hour_end = Column(Time, nullable=False)
    homepage = Column(Integer)
    timezone = Column(String(128), nullable=False, server_default='')
    default_delta = Column(String(16), nullable=False, server_default='0')

    monday = Column(SmallInteger, nullable=False, server_default=text('0'))
    tuesday = Column(SmallInteger, nullable=False, server_default=text('0'))
    wednesday = Column(SmallInteger, nullable=False, server_default=text('0'))
    thursday = Column(SmallInteger, nullable=False, server_default=text('0'))
    friday = Column(SmallInteger, nullable=False, server_default=text('0'))
    saturday = Column(SmallInteger, nullable=False, server_default=text('0'))
    sunday = Column(SmallInteger, nullable=False, server_default=text('0'))

    period1 = Column(String(16), nullable=False, server_default='0')
    period2 = Column(String(16), nullable=False, server_default='0')
    period3 = Column(String(16), nullable=False, server_default='0')
    period4 = Column(String(16), nullable=False, server_default='0')
    period5 = Column(String(16), nullable=False, server_default='0')

    dbegcache = Column(Integer, server_default='0')
    dendcache = Column(Integer, server_default='0')
    dgenercache = Column(Integer, server_default='0')
    dcreate = Column(Integer, server_default='0')
    dupdate = Column(Integer, server_default='0')
    disable = Column(SmallInteger, nullable=False, server_default=text('0'))

    description = Column(Text)
