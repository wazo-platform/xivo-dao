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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Session(Base):

    __tablename__ = 'session'
    __table_args__ = (
        PrimaryKeyConstraint('sessid'),
        Index('session__idx__expire', 'expire'),
        Index('session__idx__identifier', 'identifier'),
    )

    sessid = Column(String(32), nullable=False)
    start = Column(Integer, nullable=False)
    expire = Column(Integer, nullable=False)
    identifier = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)
