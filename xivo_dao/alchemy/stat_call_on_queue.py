# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import String, DateTime, Integer, Enum
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_manager import Base


class StatCallOnQueue(Base):

    __tablename__ = 'stat_call_on_queue'
    __table_args__ = (
        Index('stat_call_on_queue__idx_callid', 'callid'),
        Index('stat_call_on_queue__idx__stat_queue_id', 'stat_queue_id'),
        Index('stat_call_on_queue__idx__stat_agent_id', 'stat_agent_id'),
    )

    id = Column(Integer, primary_key=True)
    callid = Column(String(32), nullable=False)
    time = Column(DateTime(timezone=True), nullable=False)
    ringtime = Column(Integer, nullable=False, server_default='0')
    talktime = Column(Integer, nullable=False, server_default='0')
    waittime = Column(Integer, nullable=False, server_default='0')
    status = Column(Enum('full',
                         'closed',
                         'joinempty',
                         'leaveempty',
                         'divert_ca_ratio',
                         'divert_waittime',
                         'answered',
                         'abandoned',
                         'timeout',
                         name='call_exit_type',
                         metadata=Base.metadata),
                    nullable=False)
    stat_queue_id = Column(Integer, ForeignKey("stat_queue.id"))
    stat_agent_id = Column(Integer, ForeignKey("stat_agent.id"))

    stat_queue = relationship(StatQueue, foreign_keys=stat_queue_id)
    stat_agent = relationship(StatAgent, foreign_keys=stat_agent_id)
