# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AgentFeatures(Base):
    __tablename__ = 'agentfeatures'
    __table_args__ = (
        UniqueConstraint('number', 'tenant_uuid'),
        Index('agentfeatures__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, primary_key=True)
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    firstname = Column(String(128))
    lastname = Column(String(128))
    number = Column(String(40), nullable=False)
    passwd = Column(String(128))
    context = Column(String(79))
    language = Column(String(20))
    autologoff = Column(Integer)
    group = Column(String(255))
    description = Column(Text)
    preprocess_subroutine = Column(String(79))

    func_keys = relationship('FuncKeyDestAgent', cascade='all, delete-orphan')

    queue_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'queue',
                            QueueMember.usertype == 'agent',
                            QueueMember.userid == AgentFeatures.id)""",
        foreign_keys='QueueMember.userid',
        cascade='all, delete-orphan',
        overlaps='group_members,queue_members,agent,user',
    )

    agent_queue_skills = relationship(
        'AgentQueueSkill',
        primaryjoin='AgentQueueSkill.agentid == AgentFeatures.id',
        foreign_keys='AgentQueueSkill.agentid',
        cascade='all, delete-orphan',
        back_populates='agent',
    )

    users = relationship(
        "UserFeatures",
        primaryjoin="AgentFeatures.id == UserFeatures.agentid",
        foreign_keys='UserFeatures.agentid',
        viewonly=True,
    )
