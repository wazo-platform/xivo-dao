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

from sqlalchemy.schema import Column, Sequence
from sqlalchemy.types import Integer, Text, String
from xivo_dao.helpers.db_manager import Base


class CtiDirectories(Base):

    __tablename__ = 'ctidirectories'

    id = Column(Integer, Sequence('ctidirectories_id_seq'), primary_key=True)
    name = Column(String(255))
    uri = Column(String(255))
    delimiter = Column(String(20))
    match_direct = Column(Text, nullable=False)
    match_reverse = Column(Text, nullable=False)
    description = Column(String(255))
    deletable = Column(Integer)
