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

from sqlalchemy.schema import Column, UniqueConstraint, Index
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AccessWebService(Base):

    __tablename__ = 'accesswebservice'
    __table_args__ = (
        UniqueConstraint('name'),
        Index('accesswebservice__idx__disable', 'disable'),
        Index('accesswebservice__idx__host', 'host'),
        Index('accesswebservice__idx__login', 'login'),
        Index('accesswebservice__idx__passwd', 'passwd')
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, server_default='')
    login = Column(String(64))
    passwd = Column(String(64))
    host = Column(String(255))
    obj = Column(Text, nullable=False)
    disable = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)
