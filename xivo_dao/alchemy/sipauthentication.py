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

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum


class SIPAuthentication(Base):

    __tablename__ = 'sipauthentication'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('sipauthentication__idx__usersip_id', 'usersip_id')
    )

    id = Column(Integer, nullable=False)
    usersip_id = Column(Integer)
    user = Column(String(255), nullable=False)
    secretmode = Column(Enum('md5',
                             'clear',
                             name='sipauthentication_secretmode',
                             metadata=Base.metadata), nullable=False)
    secret = Column(String(255), nullable=False)
    realm = Column(String(1024), nullable=False)
