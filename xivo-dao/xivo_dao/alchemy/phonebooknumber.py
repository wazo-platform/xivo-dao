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

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Enum
from xivo_dao.alchemy.base import Base, Type


class PhonebookNumber(Base):

    __tablename__ = 'phonebooknumber'

    id = Column(Integer, nullable=False, primary_key=True)
    phonebookid = Column(Integer, nullable=False)
    number = Column(String(40), nullable=False, default='')
    type = Column(Enum(('home', 'office', 'other'), name='phonebookaddress_type', metadata=Type.metadata),
                  nullable=False)
