# Copyright 2007-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Boolean, DateTime, Integer, String

from xivo_dao.helpers.db_manager import Base


class AgentLoginStatus(Base):
    __tablename__ = 'agent_login_status'
    __table_args__ = (
        PrimaryKeyConstraint('agent_id'),
        UniqueConstraint('extension', 'context'),
        UniqueConstraint('interface'),
        Index('agent_login_status__idx__agent_id', 'agent_id'),
    )

    agent_id = Column(Integer, autoincrement=False, foreign_keys='agent_features.id')
    agent_number = Column(String(40), nullable=False)
    extension = Column(String(80), nullable=False)
    context = Column(String(79), nullable=False)
    interface = Column(String(128), nullable=False)
    state_interface = Column(String(128), nullable=False)
    paused = Column(Boolean, nullable=False, server_default='false')
    paused_reason = Column(String(80))
    login_at = Column(
        DateTime,
        nullable=False,
        server_default=text("(current_timestamp at time zone 'utc')"),
    )

    agent = relationship(
        'AgentFeatures',
        primaryjoin='AgentLoginStatus.agent_id == AgentFeatures.id',
        foreign_keys='AgentFeatures.id',
        uselist=False,
    )
