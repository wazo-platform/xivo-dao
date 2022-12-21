# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AgentMembershipStatus(Base):

    __tablename__ = 'agent_membership_status'
    __table_args__ = (
        PrimaryKeyConstraint('agent_id', 'queue_id'),
    )

    agent_id = Column(Integer, autoincrement=False)
    queue_id = Column(Integer, autoincrement=False)
    queue_name = Column(String(128), nullable=False)
    penalty = Column(Integer, nullable=False, server_default='0')
