# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import String, Integer, Text

from xivo_dao.helpers.db_manager import Base


class QueueLog(Base):

    __tablename__ = 'queue_log'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('queue_log__idx_agent', 'agent'),
        Index('queue_log__idx_callid', 'callid'),
        Index('queue_log__idx_event', 'event'),
        Index('queue_log__idx_time', 'time'),
    )

    time = Column(String(26), nullable=False, server_default='')
    callid = Column(String(32), nullable=False, server_default='')
    queuename = Column(String(50), nullable=False, server_default='')
    agent = Column(String(50), nullable=False, server_default='')
    event = Column(String(20), nullable=False, server_default='')
    data1 = Column(Text, server_default='')
    data2 = Column(Text, server_default='')
    data3 = Column(Text, server_default='')
    data4 = Column(Text, server_default='')
    data5 = Column(Text, server_default='')
    id = Column(Integer)
