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

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Enum
from xivo_dao.helpers.db_manager import Base, Type


class Callfiltermember(Base):

    __tablename__ = 'callfiltermember'

    id = Column(Integer, primary_key=True)
    callfilterid = Column(Integer, ForeignKey('callfilter.id'))
    type = Column(Enum('user',
                       name='callfiltermember_type',
                       metadata=Type.metadata),
                  nullable=False)
    typeval = Column(String(128), nullable=False, default=0)
    ringseconds = Column(Integer, nullable=False, default=0)
    priority = Column(Integer, nullable=False, default=0)
    bstype = Column(Enum('boss', 'secretary',
                         name='generic_bsfilter',
                         metadata=Type.metadata),
                    nullable=False)
    active = Column(Integer, nullable=False, default=0)
