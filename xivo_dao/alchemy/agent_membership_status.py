# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AgentMembershipStatus(Base):
    __tablename__ = 'agent_membership_status'
    __table_args__ = (
        PrimaryKeyConstraint('agent_id', 'queue_id'),
        Index('agent_membership_status__idx__agent_id', 'agent_id'),
        Index('agent_membership_status__idx__queue_id', 'queue_id'),
    )

    agent_id = Column(
        Integer, ForeignKey('agentfeatures.id', ondelete='CASCADE'), autoincrement=False
    )
    queue_id = Column(
        Integer, ForeignKey('queuefeatures.id', ondelete='CASCADE'), autoincrement=False
    )
    queue_name = Column(String(128), nullable=False)
    penalty = Column(Integer, nullable=False, server_default='0')
