# -*- coding: utf-8 -*-

from sqlalchemy.schema import Column, ForeignKey, Sequence
from sqlalchemy.types import Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTERVAL
from xivo_dao.alchemy.base import Base


class StatAgentPeriodic(Base):

    __tablename__ = 'stat_agent_periodic'

    id = Column(Integer, Sequence('stat_queue_periodic_id_seq'), primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    login_time = Column(INTERVAL, nullable=False, default=0)
    agent_id = Column(Integer, ForeignKey("stat_agent.id"))
