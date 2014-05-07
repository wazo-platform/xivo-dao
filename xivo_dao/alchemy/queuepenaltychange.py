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

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, Enum

from xivo_dao.helpers.db_manager import Base


class QueuePenaltyChange(Base):

    __tablename__ = 'queuepenaltychange'
    __table_args__ = (
        PrimaryKeyConstraint('queuepenalty_id', 'seconds'),
    )

    queuepenalty_id = Column(Integer, nullable=False, autoincrement=False)
    seconds = Column(Integer, nullable=False, server_default='0', autoincrement=False)
    maxp_sign = Column(Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata))
    maxp_value = Column(Integer)
    minp_sign = Column(Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata))
    minp_value = Column(Integer)
