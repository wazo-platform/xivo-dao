# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class QueueInfo(Base):

    __tablename__ = 'queue_info'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('queue_info_call_time_t_index', 'call_time_t'),
        Index('queue_info_queue_name_index', 'queue_name'),
    )

    id = Column(Integer)
    call_time_t = Column(Integer)
    queue_name = Column(String(128), nullable=False, server_default='')
    caller = Column(String(80), nullable=False, server_default='')
    caller_uniqueid = Column(String(32), nullable=False, server_default='')
    call_picker = Column(String(80))
    hold_time = Column(Integer)
    talk_time = Column(Integer)
