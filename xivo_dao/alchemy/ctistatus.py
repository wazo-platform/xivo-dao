# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiStatus(Base):

    __tablename__ = 'ctistatus'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('presence_id', 'name'),
    )

    id = Column(Integer)
    presence_id = Column(Integer, ForeignKey('ctipresences.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    actions = Column(String(255))
    color = Column(String(20))
    access_status = Column(String(255))
    deletable = Column(Integer)
