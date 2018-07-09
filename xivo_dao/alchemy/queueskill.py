# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .queueskillcat import QueueSkillCat


class QueueSkill(Base):

    __tablename__ = 'queueskill'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    catid = Column(Integer)
    name = Column(String(64), server_default='', nullable=False)
    description = Column(Text)

    queue_skill_cat = relationship(
        'QueueSkillCat',
        primaryjoin='QueueSkillCat.id == QueueSkill.catid',
        foreign_keys='QueueSkill.catid',
        cascade='save-update,merge',
    )

    @hybrid_property
    def category(self):
        return getattr(self.queue_skill_cat, 'name', None)

    @category.setter
    def category(self, value):
        if value is None:
            self.queue_skill_cat = None
            return

        # Allow QueueSkill(category=value)
        session = object_session(self)
        if not session:
            self.queue_skill_cat = QueueSkillCat(name=value)
            return

        category = session.query(QueueSkillCat).filter_by(name=value).first()
        if not category:
            category = QueueSkillCat(name=value)
        self.queue_skill_cat = category
