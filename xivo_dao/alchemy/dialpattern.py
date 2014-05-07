# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from sqlalchemy.schema import Column, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class DialPattern(Base):

    __tablename__ = 'dialpattern'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('type', 'typeid')
    )

    id = Column(Integer)
    type = Column(String(32), nullable=False)
    typeid = Column(Integer, nullable=False)
    externprefix = Column(String(64))
    prefix = Column(String(32))
    exten = Column(String(40), nullable=False)
    stripnum = Column(Integer)
    callerid = Column(String(80))
