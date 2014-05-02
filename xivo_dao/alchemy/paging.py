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


class Paging(Base):

    __tablename__ = 'paging'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('number'),
    )

    id = Column(Integer, nullable=False)
    number = Column(String(32))
    duplex = Column(Integer, nullable=False, server_default='0')
    ignore = Column(Integer, nullable=False, server_default='0')
    record = Column(Integer, nullable=False, server_default='0')
    quiet = Column(Integer, nullable=False, server_default='0')
    timeout = Column(Integer, nullable=False)
    announcement_file = Column(String(64))
    announcement_play = Column(Integer, nullable=False, server_default='0')
    announcement_caller = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
