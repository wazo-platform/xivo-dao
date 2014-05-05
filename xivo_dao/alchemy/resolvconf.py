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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Resolvconf(Base):

    __tablename__ = 'resolvconf'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('domain'),
    )

    id = Column(Integer, nullable=False)
    hostname = Column(String(63), nullable=False, server_default='xivo')
    domain = Column(String(255), nullable=False, server_default='')
    nameserver1 = Column(String(255))
    nameserver2 = Column(String(255))
    nameserver3 = Column(String(255))
    search = Column(String(255))
    description = Column(Text)
