# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy import sql
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Entity(Base):

    __tablename__ = 'entity'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    name = Column(String(64), nullable=False, server_default='')
    displayname = Column(String(128), nullable=False, server_default='')
    phonenumber = Column(String(40), nullable=False, server_default='')
    faxnumber = Column(String(40), nullable=False, server_default='')
    email = Column(String(255), nullable=False, server_default='')
    url = Column(String(255), nullable=False, server_default='')
    address1 = Column(String(30), nullable=False, server_default='')
    address2 = Column(String(30), nullable=False, server_default='')
    city = Column(String(128), nullable=False, server_default='')
    state = Column(String(128), nullable=False, server_default='')
    zipcode = Column(String(16), nullable=False, server_default='')
    country = Column(String(3), nullable=False, server_default='')
    disable = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)

    @classmethod
    def query_default_id(cls):
        return sql.select([cls.id]).limit(1)

    @classmethod
    def query_default_name(cls):
        return sql.select([cls.name]).limit(1)
