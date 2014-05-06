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

from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Enum, Text

from xivo_dao.helpers.db_manager import Base


class Callfilter(Base):

    __tablename__ = 'callfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('callfilter__uidx__name', 'name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False, server_default='')
    type = Column(Enum('bosssecretary',
                       name='callfilter_type',
                       metadata=Base.metadata),
                  nullable=False)
    bosssecretary = Column(Enum('bossfirst-serial',
                                'bossfirst-simult',
                                'secretary-serial',
                                'secretary-simult',
                                'all',
                                name='callfilter_bosssecretary',
                                metadata=Base.metadata))
    callfrom = Column(Enum('internal', 'external', 'all',
                           name='callfilter_callfrom',
                           metadata=Base.metadata))
    ringseconds = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)
