# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import re

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, String, Enum

interface_regex = re.compile(r'Local/(?P<exten>.*)@(?P<context>.*)')


class QueueMember(Base):

    __tablename__ = 'queuemember'
    __table_args__ = (
        PrimaryKeyConstraint('queue_name', 'interface'),
        UniqueConstraint('queue_name', 'channel', 'interface', 'usertype', 'userid', 'category', 'position'),
        Index('queuemember__idx__category', 'category'),
        Index('queuemember__idx__channel', 'channel'),
        Index('queuemember__idx__userid', 'userid'),
        Index('queuemember__idx__usertype', 'usertype'),
    )

    queue_name = Column(String(128))
    interface = Column(String(128))
    penalty = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    usertype = Column(Enum('agent', 'user', name='queuemember_usertype', metadata=Base.metadata), nullable=False)
    userid = Column(Integer, nullable=False)
    channel = Column(String(25), nullable=False)
    category = Column(Enum('queue', 'group', name='queue_category', metadata=Base.metadata), nullable=False)
    position = Column(Integer, nullable=False, server_default='0')

    agent = relationship(
        'AgentFeatures',
        primaryjoin="""and_(QueueMember.usertype == 'agent',
                            QueueMember.userid == AgentFeatures.id)""",
        foreign_keys='QueueMember.userid',
    )

    user = relationship(
        'UserFeatures',
        primaryjoin="""and_(QueueMember.usertype == 'user',
                            QueueMember.userid == UserFeatures.id)""",
        foreign_keys='QueueMember.userid',
    )

    group = relationship(
        'GroupFeatures',
        primaryjoin="""and_(QueueMember.category == 'group',
                            QueueMember.queue_name == GroupFeatures.name)""",
        foreign_keys='QueueMember.queue_name',
    )

    queue = relationship(
        'QueueFeatures',
        primaryjoin='QueueMember.queue_name == QueueFeatures.name',
        foreign_keys='QueueMember.queue_name',
        viewonly=True,
    )

    def fix(self):
        if self.user:
            self._fix_user(self.user)
        elif self.agent:
            self._fix_agent(self.agent)

    def _fix_user(self, user):
        if not user.lines:
            return

        main_line = user.lines[0]
        if main_line.endpoint_sip:
            self.channel = 'SIP'
            self.interface = '{}/{}'.format(self.channel, main_line.endpoint_sip.name)

        elif main_line.endpoint_sccp:
            self.channel = 'SCCP'
            self.interface = '{}/{}'.format(self.channel, main_line.endpoint_sccp.name)

        elif main_line.endpoint_custom:
            self.channel = '**Unknown**'
            self.interface = main_line.endpoint_custom.interface

    def _fix_agent(self, agent):
        self.channel = 'Agent'
        self.interface = '{}/{}'.format(self.channel, agent.number)

    @hybrid_property
    def priority(self):
        return self.position

    @priority.setter
    def priority(self, value):
        self.position = value

    @property
    def exten(self):
        match = re.search(interface_regex, self.interface)
        if match:
            return match.group('exten')

    @property
    def context(self):
        match = re.search(interface_regex, self.interface)
        if match:
            return match.group('context')
