# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from sqlalchemy.schema import Column, ForeignKey, Sequence
from sqlalchemy.types import Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTERVAL
from xivo_dao.helpers.db_manager import Base


class StatAgentPeriodic(Base):

    __tablename__ = 'stat_agent_periodic'

    id = Column(Integer, Sequence('stat_queue_periodic_id_seq'), primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    login_time = Column(INTERVAL, nullable=False, default=0)
    pause_time = Column(INTERVAL, nullable=False, default=0)
    wrapup_time = Column(INTERVAL, nullable=False, default=0)
    agent_id = Column(Integer, ForeignKey("stat_agent.id"))
