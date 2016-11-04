# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.queue import Queue
from xivo_dao.helpers.db_manager import Base


class GroupFeatures(Base):

    __tablename__ = 'groupfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('groupfeatures__idx__context', 'context'),
        Index('groupfeatures__idx__name', 'name'),
        Index('groupfeatures__idx__number', 'number'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    number = Column(String(40))
    context = Column(String(39))
    transfer_user = Column(Integer, nullable=False, server_default='0')
    transfer_call = Column(Integer, nullable=False, server_default='0')
    write_caller = Column(Integer, nullable=False, server_default='0')
    write_calling = Column(Integer, nullable=False, server_default='0')
    ignore_forward = Column(Integer, nullable=False, server_default='1')
    timeout = Column(Integer)
    preprocess_subroutine = Column(String(39))
    deleted = Column(Integer, nullable=False, server_default='0')

    extensions = relationship('Extension',
                              primaryjoin="""and_(Extension.type == 'group',
                                                  Extension.typeval == cast(GroupFeatures.id, String))""",
                              viewonly=True,
                              foreign_keys='Extension.typeval')

    queue = relationship('Queue',
                         primaryjoin="""and_(Queue.category == 'group',
                                             Queue.name == GroupFeatures.name)""",
                         uselist=False,
                         cascade='all, delete-orphan',
                         foreign_keys='Queue.name')

    ringinuse = association_proxy('queue', 'ringinuse')
    ring_strategy = association_proxy('queue', 'strategy')
    user_timeout = association_proxy('queue', 'timeout')
    retry_delay = association_proxy('queue', 'retry')
    commented = association_proxy('queue', 'commented')

    def __init__(self, **kwargs):
        retry = kwargs.pop('retry_delay', 5)
        ringinuse = int(kwargs.pop('ring_in_use', 1))
        strategy = kwargs.pop('ring_strategy', 'ringall')
        timeout = kwargs.pop('user_timeout', 15)
        commented = int(not(kwargs.pop('enabled', True)))
        super(GroupFeatures, self).__init__(**kwargs)
        if not self.queue:
            self.queue = Queue(retry=retry,
                               ringinuse=ringinuse,
                               strategy=strategy,
                               timeout=timeout,
                               commented=commented,
                               queue_youarenext='queue-youarenext',
                               queue_thereare='queue-thereare',
                               queue_callswaiting='queue-callswaiting',
                               queue_holdtime='queue-holdtime',
                               queue_minutes='queue-minutes',
                               queue_seconds='queue-seconds',
                               queue_thankyou='queue-thankyou',
                               queue_reporthold='queue-reporthold',
                               periodic_announce='queue-periodic-announce',
                               announce_frequency=0,
                               periodic_announce_frequency=0,
                               announce_round_seconds=0,
                               announce_holdtime='no',
                               wrapuptime=0,
                               maxlen=0,
                               memberdelay=0,
                               weight=0,
                               category='group',
                               autofill=1,
                               announce_position='no')

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0) if value is not None else None

    @hybrid_property
    def ring_in_use(self):
        return bool(self.ringinuse)

    @ring_in_use.setter
    def ring_in_use(self, value):
        self.ringinuse = int(value)

    def fix(self):
        for extension in self.extensions:
            self.number = extension.exten
            self.context = extension.context
            if self.queue:
                self.queue.context = extension.context
            return

        self.number = None
        self.context = None
        if self.queue:
            self.queue.context = None
