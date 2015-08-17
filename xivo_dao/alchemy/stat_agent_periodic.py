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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint,\
    Index
from sqlalchemy.types import Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_manager import Base


class StatAgentPeriodic(Base):

    __tablename__ = 'stat_agent_periodic'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('agent_id',),
                             ('stat_agent.id',)),
        Index('stat_agent_periodic__idx__agent_id', 'agent_id'),
        Index('stat_agent_periodic__idx__time', 'time'),
    )

    id = Column(Integer)
    time = Column(TIMESTAMP, nullable=False)
    login_time = Column(INTERVAL, nullable=False, server_default='0')
    pause_time = Column(INTERVAL, nullable=False, server_default='0')
    wrapup_time = Column(INTERVAL, nullable=False, server_default='0')
    agent_id = Column(Integer)

    stat_agent = relationship(StatAgent, foreign_keys=agent_id)
