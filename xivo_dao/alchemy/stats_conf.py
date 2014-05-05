# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index, \
    UniqueConstraint
from sqlalchemy.types import Integer, String, Text, TIMESTAMP, SmallInteger

from xivo_dao.helpers.db_manager import Base


class StasConf(Base):

    __tablename__ = 'stats_conf'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('stats_conf__idx__disable', 'disable'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, server_default='')
    hour_start = Column(TIMESTAMP, nullable=False)
    hour_end = Column(TIMESTAMP, nullable=False)
    homepage = Column(Integer)
    timezone = Column(String(128), nullable=False, server_default='')
    default_delta = Column(String(16), nullable=False, server_default='0')

    monday = Column(SmallInteger, nullable=False, server_default='0')
    tuesday = Column(SmallInteger, nullable=False, server_default='0')
    wednesday = Column(SmallInteger, nullable=False, server_default='0')
    thursday = Column(SmallInteger, nullable=False, server_default='0')
    friday = Column(SmallInteger, nullable=False, server_default='0')
    saturday = Column(SmallInteger, nullable=False, server_default='0')
    sunday = Column(SmallInteger, nullable=False, server_default='0')

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
    disable = Column(SmallInteger, nullable=False, server_default='0')

    description = Column(Text)
