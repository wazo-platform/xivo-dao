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

from sqlalchemy.schema import Column, UniqueConstraint, Index, \
    PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class Extension(Base):

    __tablename__ = 'extensions'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('exten', 'context'),
        Index('extensions__idx__context', 'context'),
        Index('extensions__idx__exten', 'exten'),
        Index('extensions__idx__type', 'type'),
        Index('extensions__idx__typeval', 'typeval'),
    )

    id = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    context = Column(String(39), nullable=False, server_default='')
    exten = Column(String(40), nullable=False, server_default='')
    type = Column(enum.extenumbers_type, nullable=False)
    typeval = Column(String(255), nullable=False, server_default='')

    @property
    def name(self):
        return self.typeval
