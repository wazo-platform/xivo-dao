# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Enum, Integer, String

from xivo_dao.helpers.db_manager import Base

interface_regex = re.compile(r'Local/(?P<exten>.*)@(?P<context>.*)')


class QueueMember(Base):
    __tablename__ = 'queuemember'
    __table_args__ = (
        PrimaryKeyConstraint('queue_name', 'interface'),
        UniqueConstraint(
            'queue_name',
            'channel',
            'interface',
            'usertype',
            'userid',
            'category',
            'position',
        ),
        Index('queuemember__idx__category', 'category'),
        Index('queuemember__idx__channel', 'channel'),
        Index('queuemember__idx__userid', 'userid'),
        Index('queuemember__idx__usertype', 'usertype'),
    )

    queue_name = Column(String(128))
    interface = Column(String(128))
    penalty = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    usertype = Column(
        Enum('agent', 'user', name='queuemember_usertype', metadata=Base.metadata),
        nullable=False,
    )
    userid = Column(Integer, nullable=False)
    channel = Column(String(25), nullable=False)
    category = Column(
        Enum('queue', 'group', name='queue_category', metadata=Base.metadata),
        nullable=False,
    )
    position = Column(Integer, nullable=False, server_default='0')

    agent = relationship(
        'AgentFeatures',
        primaryjoin="""and_(QueueMember.usertype == 'agent',
                            QueueMember.userid == AgentFeatures.id)""",
        foreign_keys='QueueMember.userid',
        overlaps='queue_queue_members,group_members,queue_members,user',
    )

    user = relationship(
        'UserFeatures',
        primaryjoin="""and_(QueueMember.usertype == 'user',
                            QueueMember.userid == UserFeatures.id)""",
        foreign_keys='QueueMember.userid',
        overlaps='queue_queue_members,group_members,queue_members,agent',
    )

    group = relationship(
        'GroupFeatures',
        primaryjoin="""and_(QueueMember.category == 'group',
                            QueueMember.queue_name == GroupFeatures.name)""",
        foreign_keys='QueueMember.queue_name',
        overlaps=(
            'agent_queue_members,'
            'extension_queue_members,'
            'user_queue_members,'
        ),  # fmt: skip
    )
    users_from_call_pickup_group_interceptor_user_targets = association_proxy(
        'group', 'users_from_call_pickup_user_targets'
    )
    users_from_call_pickup_group_interceptor_group_targets = association_proxy(
        'group', 'users_from_call_pickup_group_targets'
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
        else:
            self._fix_local()

    def _fix_user(self, user):
        if not user.lines:
            return

        main_line = user.lines[0]
        if main_line.endpoint_sip:
            self.channel = 'SIP'
            self.interface = f'PJSIP/{main_line.endpoint_sip.name}'

        elif main_line.endpoint_sccp:
            self.channel = 'SCCP'
            self.interface = f'{self.channel}/{main_line.endpoint_sccp.name}'

        elif main_line.endpoint_custom:
            self.channel = '**Unknown**'
            self.interface = main_line.endpoint_custom.interface

    def _fix_agent(self, agent):
        self.channel = 'Agent'
        self.interface = f'{self.channel}/{agent.number}'

    def _fix_local(self):
        self.channel = 'Local'
        self.interface = f'{self.channel}/{self.exten}@{self.context}'

    @hybrid_property
    def priority(self):
        return self.position

    @priority.setter
    def priority(self, value):
        self.position = value

    @property
    def exten(self):
        if hasattr(self, '_exten'):
            return self._exten

        match = re.search(interface_regex, self.interface or '')
        if match:
            return match.group('exten')

    @exten.setter
    def exten(self, value):
        self._exten = value

    @property
    def context(self):
        if hasattr(self, '_context'):
            return self._context

        match = re.search(interface_regex, self.interface or '')
        if match:
            return match.group('context')

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def extension(self):
        return self

    @extension.setter
    def extension(self, extension):
        self.exten = extension.exten
        self.context = extension.context
