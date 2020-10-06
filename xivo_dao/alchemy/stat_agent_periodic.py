# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, Index, ForeignKey
from sqlalchemy.types import Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_manager import Base


class StatAgentPeriodic(Base):

    __tablename__ = 'stat_agent_periodic'
    __table_args__ = (
        Index('stat_agent_periodic__idx__stat_agent_id', 'stat_agent_id'),
        Index('stat_agent_periodic__idx__time', 'time'),
    )

    id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    login_time = Column(INTERVAL, nullable=False, server_default='0')
    pause_time = Column(INTERVAL, nullable=False, server_default='0')
    wrapup_time = Column(INTERVAL, nullable=False, server_default='0')
    stat_agent_id = Column(Integer, ForeignKey("stat_agent.id"))

    stat_agent = relationship(StatAgent, foreign_keys=stat_agent_id)
