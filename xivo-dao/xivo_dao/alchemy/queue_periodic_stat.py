# -*- coding: utf-8 -*-

# Copyright (C) 2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, TIMESTAMP
from xivo_dao.alchemy.base import Base


class QueuePeriodicStat(Base):

    __tablename__ = 'queue_periodic_stat'

    id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    answered = Column(Integer, nullable=False, default=0)
    abandoned = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    full = Column(Integer, nullable=False, default=0)
    closed = Column(Integer, nullable=False, default=0)
    joinempty = Column(Integer, nullable=False, default=0)
    leaveempty = Column(Integer, nullable=False, default=0)
    reroutedguide = Column(Integer, nullable=False, default=0)
    retoutednumber = Column(Integer, nullable=False, default=0)
    timeout = Column(Integer, nullable=False, default=0)
    queue_id = Column(Integer, ForeignKey("queuefeatures.id"))
