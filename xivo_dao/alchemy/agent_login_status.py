# -*- coding: utf-8 -*-

# Copyright (C) 2007-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text
from sqlalchemy.schema import Column, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, DateTime, Boolean

from xivo_dao.helpers.db_manager import Base


class AgentLoginStatus(Base):

    __tablename__ = 'agent_login_status'
    __table_args__ = (
        PrimaryKeyConstraint('agent_id'),
        UniqueConstraint('extension', 'context'),
        UniqueConstraint('interface')
    )

    agent_id = Column(Integer, autoincrement=False)
    agent_number = Column(String(40), nullable=False)
    extension = Column(String(80), nullable=False)
    context = Column(String(80), nullable=False)
    interface = Column(String(128), nullable=False)
    state_interface = Column(String(128), nullable=False)
    paused = Column(Boolean, nullable=False, server_default='false')
    paused_reason = Column(String(80))
    login_at = Column(DateTime, nullable=False, server_default=text("(current_timestamp at time zone 'utc')"))
