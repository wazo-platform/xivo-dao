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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class GroupFeatures(Base):

    __tablename__ = 'groupfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('groupfeatures__idx__context', 'context'),
        Index('groupfeatures__idx__name', 'name'),
        Index('groupfeatures__idx__number', 'number'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    number = Column(String(40), nullable=False, server_default='')
    context = Column(String(39), nullable=False)
    transfer_user = Column(Integer, nullable=False, server_default='0')
    transfer_call = Column(Integer, nullable=False, server_default='0')
    write_caller = Column(Integer, nullable=False, server_default='0')
    write_calling = Column(Integer, nullable=False, server_default='0')
    ignore_forward = Column(Integer, nullable=False, server_default='1')
    timeout = Column(Integer)
    preprocess_subroutine = Column(String(39))
    deleted = Column(Integer, nullable=False, server_default='0')
