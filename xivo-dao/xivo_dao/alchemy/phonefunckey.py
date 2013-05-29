# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from sqlalchemy.types import Integer, String
from xivo_dao.helpers.db_manager import Base


class PhoneFunckey(Base):
    __tablename__ = 'phonefunckey'

    iduserfeatures = Column(Integer, primary_key=True)
    fknum = Column(Integer, primary_key=True)
    exten = Column(String(40))
    typevalextenumbers = Column(String(255))
    typevalextenumbersright = Column(String(255))
    label = Column(String(32))
    typeextenumbers = Column(String(16))
    supervision = Column(Integer, nullable=False, default=0)
    progfunckey = Column(Integer, nullable=False, default=0)
    typeextenumbersright = Column(String(16))
