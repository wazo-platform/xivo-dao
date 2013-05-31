# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.helpers.db_manager import Base, Type

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Enum


class ContextNumbers(Base):

    __tablename__ = 'contextnumbers'

    context = Column(String(39), primary_key=True)
    type = Column(Enum('user', 'group', 'queue', 'meetme', 'incall',
                       name='contextnumbers_type',
                       metadata=Type.metadata),
                  primary_key=True)
    numberbeg = Column(String(16), default=0, primary_key=True)
    numberbeg = Column(String(16), default=0, primary_key=True)
    didlength = Column(Integer, nullable=False, default=0)
