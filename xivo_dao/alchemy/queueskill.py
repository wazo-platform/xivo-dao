# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import select
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .queueskillcat import QueueSkillCat


class QueueSkill(Base):

    __tablename__ = 'queueskill'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name', 'tenant_uuid'),
        Index('queueskill__idx__tenant_uuid', 'tenant_uuid'),
        {
            'comment': 'Skills-based routing (SBR), or Skills-based call '
                       'routing, is a call-assignment strategy used in '
                       'call centres to assign incoming calls to the most '
                       'suitable agent, instead of simply choosing the '
                       'next available agent. Skills-based routing is '
                       'also based on call distribution to agents through '
                       'waiting queues, but one or many skills can be '
                       'assigned to each agent, and call can be '
                       'distributed to the most suitable agent.'
        }
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    catid = Column(Integer)
    name = Column(String(64), server_default='', nullable=False)
    description = Column(Text)

    queue_skill_cat = relationship(
        'QueueSkillCat',
        primaryjoin='QueueSkillCat.id == QueueSkill.catid',
        foreign_keys='QueueSkill.catid',
        cascade='save-update,merge',
    )

    agent_queue_skills = relationship(
        'AgentQueueSkill',
        primaryjoin='AgentQueueSkill.skillid == QueueSkill.id',
        foreign_keys='AgentQueueSkill.skillid',
        cascade='all, delete-orphan',
    )

    @hybrid_property
    def category(self):
        return getattr(self.queue_skill_cat, 'name', None)

    @category.expression
    def category(cls):
        return select([QueueSkillCat.name]).where(QueueSkillCat.id == cls.catid).as_scalar()

    @category.setter
    def category(self, value):
        self._category = value
