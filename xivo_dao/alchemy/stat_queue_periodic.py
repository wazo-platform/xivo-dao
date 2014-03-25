# -*- coding: utf-8 -*-
#
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
from sqlalchemy.types import Integer, TIMESTAMP
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base


class StatQueuePeriodic(Base):

    __tablename__ = 'stat_queue_periodic'

    id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    answered = Column(Integer, nullable=False, server_default='0')
    abandoned = Column(Integer, nullable=False, server_default='0')
    total = Column(Integer, nullable=False, server_default='0')
    full = Column(Integer, nullable=False, server_default='0')
    closed = Column(Integer, nullable=False, server_default='0')
    joinempty = Column(Integer, nullable=False, server_default='0')
    leaveempty = Column(Integer, nullable=False, server_default='0')
    divert_ca_ratio = Column(Integer, nullable=False, server_default='0')
    divert_waittime = Column(Integer, nullable=False, server_default='0')
    timeout = Column(Integer, nullable=False, server_default='0')
    queue_id = Column(Integer, ForeignKey("stat_queue.id"))

    stat_queue = relationship("StatQueue", foreign_keys=queue_id)
