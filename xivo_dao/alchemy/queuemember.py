# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (Column,
                               Index,
                               PrimaryKeyConstraint,
                               UniqueConstraint)
from sqlalchemy.types import Integer, String, Enum


class QueueMember(Base):

    __tablename__ = 'queuemember'
    __table_args__ = (
        PrimaryKeyConstraint('queue_name', 'interface'),
        UniqueConstraint('queue_name', 'channel', 'usertype', 'userid', 'category'),
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

    user = relationship('UserFeatures',
                        primaryjoin="""and_(QueueMember.usertype == 'user',
                                            QueueMember.userid == UserFeatures.id)""",
                        foreign_keys='QueueMember.userid')

    group = relationship('GroupFeatures',
                         primaryjoin="""and_(QueueMember.category == 'group',
                                             QueueMember.queue_name == GroupFeatures.name)""",
                         foreign_keys='QueueMember.queue_name')

    @hybrid_property
    def local(self):
        return self.channel == 'Local'

    @local.setter
    def local(self, value):
        if value and not (self.user and self.user.lines and self.user.lines[0].endpoint_custom):
            self.channel = 'Local'
            return

        if self.user and self.user.lines:
            main_line = self.user.lines[0]
            if main_line.endpoint_sip:
                self.channel = 'SIP'
            elif main_line.endpoint_sccp:
                self.channel = 'SCCP'
            elif main_line.endpoint_custom:
                self.channel = '**Unknown**'

    def fix(self):
        self.local = self.local
        if self.user and self.user.lines:
            main_line = self.user.lines[0]
            if main_line.endpoint_sip:
                if not self.local:
                    sub_interface = main_line.endpoint_sip.name
                elif main_line.extensions:
                    sub_interface = main_line.extensions[0].exten
                else:
                    sub_interface = ''
                self.interface = '{}/{}'.format(self.channel, sub_interface)

            elif main_line.endpoint_sccp:
                if not self.local:
                    sub_interface = main_line.endpoint_sccp.name
                elif main_line.extensions:
                    sub_interface = main_line.extensions[0].exten
                else:
                    sub_interface = ''
                self.interface = '{}/{}'.format(self.channel, sub_interface)

            elif main_line.endpoint_custom:
                self.interface = main_line.endpoint_custom.interface
