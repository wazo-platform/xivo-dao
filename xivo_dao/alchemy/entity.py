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

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, TEXT
from xivo_dao.helpers.db_manager import Base


class Entity(Base):

    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    displayname = Column(String(128), nullable=False)
    phonenumber = Column(String(40), nullable=False, default='')
    faxnumber = Column(String(40), nullable=False, default='')
    email = Column(String(255), nullable=False, default='')
    url = Column(String(255), nullable=False, default='')
    address1 = Column(String(30), nullable=False, default='')
    address2 = Column(String(30), nullable=False, default='')
    city = Column(String(128), nullable=False, default='')
    state = Column(String(128), nullable=False, default='')
    zipcode = Column(String(16), nullable=False, default='')
    country = Column(String(3), nullable=False, default='')
    disable = Column(Integer, nullable=False, default=0)
    dcreate = Column(Integer, nullable=False, default=0)
    description = Column(TEXT, nullable=False, default='')
