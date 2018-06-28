# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AgentFeatures(Base):

    __tablename__ = 'agentfeatures'
    __table_args__ = (
        UniqueConstraint('number'),
    )

    id = Column(Integer, primary_key=True)
    numgroup = Column(Integer, nullable=False)
    firstname = Column(String(128))
    lastname = Column(String(128))
    number = Column(String(40), nullable=False)
    passwd = Column(String(128))
    context = Column(String(39))
    language = Column(String(20))
    autologoff = Column(Integer)
    group = Column(String(255))
    description = Column(Text)
    preprocess_subroutine = Column(String(40))

    func_keys = relationship(
        'FuncKeyDestAgent',
        cascade='all, delete-orphan'
    )

    queue_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'queue',
                            QueueMember.usertype == 'agent',
                            QueueMember.userid == AgentFeatures.id)""",
        foreign_keys='QueueMember.userid',
        cascade='all, delete-orphan',
    )
