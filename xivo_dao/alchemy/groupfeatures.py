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
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuemember import QueueMember
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

    caller_id = relationship('Callerid',
                             primaryjoin="""and_(Callerid.type == 'group',
                                                 Callerid.typeval == GroupFeatures.id)""",
                             foreign_keys='Callerid.typeval',
                             cascade='all, delete-orphan',
                             uselist=False)

    caller_id_mode = association_proxy('caller_id', 'mode',
                                       creator=lambda _mode: Callerid(type='group',
                                                                      mode=_mode))
    caller_id_name = association_proxy('caller_id', 'name',
                                       creator=lambda _name: Callerid(type='group',
                                                                      name=_name))

    extensions = relationship('Extension',
                              primaryjoin="""and_(Extension.type == 'group',
                                                  Extension.typeval == cast(GroupFeatures.id, String))""",
                              foreign_keys='Extension.typeval',
                              viewonly=True,
                              back_populates='group')

    incall_dialactions = relationship('Dialaction',
                                      primaryjoin="""and_(Dialaction.category == 'incall',
                                           Dialaction.action == 'group',
                                           Dialaction.actionarg1 == cast(GroupFeatures.id, String))""",
                                      foreign_keys='Dialaction.actionarg1',
                                      viewonly=True)

    incalls = association_proxy('incall_dialactions', 'incall')

    group_dialactions = relationship('Dialaction',
                                     primaryjoin="""and_(Dialaction.category == 'group',
                                         Dialaction.categoryval == cast(GroupFeatures.id, String))""",
                                     cascade='all, delete-orphan',
                                     collection_class=attribute_mapped_collection('event'),
                                     foreign_keys='Dialaction.categoryval')

    group_members = relationship('QueueMember',
                                 primaryjoin="""and_(QueueMember.category == 'group',
                                                     QueueMember.queue_name == GroupFeatures.name)""",
                                 order_by='QueueMember.position',
                                 foreign_keys='QueueMember.queue_name',
                                 collection_class=ordering_list('position', count_from=1),
                                 cascade='all, delete-orphan',
                                 passive_updates=False)

    users = association_proxy('group_members', 'user',
                              creator=lambda _user: QueueMember(category='group',
                                                                usertype='user',
                                                                user=_user))

    queue = relationship('Queue',
                         primaryjoin="""and_(Queue.category == 'group',
                                             Queue.name == GroupFeatures.name)""",
                         foreign_keys='Queue.name',
                         cascade='all, delete-orphan',
                         uselist=False,
                         passive_updates=False)

    enabled = association_proxy('queue', 'enabled')
    music_on_hold = association_proxy('queue', 'musicclass')
    retry_delay = association_proxy('queue', 'retry')
    ring_in_use = association_proxy('queue', 'ring_in_use')
    ring_strategy = association_proxy('queue', 'strategy')
    user_timeout = association_proxy('queue', 'timeout')

    func_keys = relationship('FuncKeyDestGroup',
                             cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        retry = kwargs.pop('retry_delay', 5)
        ring_in_use = kwargs.pop('ring_in_use', True)
        strategy = kwargs.pop('ring_strategy', 'ringall')
        timeout = kwargs.pop('user_timeout', 15)
        musicclass = kwargs.pop('music_on_hold', None)
        enabled = kwargs.pop('enabled', True)
        super(GroupFeatures, self).__init__(**kwargs)
        if not self.queue:
            self.queue = Queue(retry=retry,
                               ring_in_use=ring_in_use,
                               strategy=strategy,
                               timeout=timeout,
                               musicclass=musicclass,
                               enabled=enabled,
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

    @property
    def fallbacks(self):
        return self.group_dialactions

    # Note: fallbacks[key] = Dialaction() doesn't pass in this method
    @fallbacks.setter
    def fallbacks(self, dialactions):
        for event in self.group_dialactions.keys():
            if event not in dialactions:
                self.group_dialactions.pop(event, None)

        for event, dialaction in dialactions.iteritems():
            if dialaction is None:
                self.group_dialactions.pop(event, None)
                return

            if event not in self.group_dialactions:
                dialaction.category = 'group'
                dialaction.linked = 1
                dialaction.event = event
                self.group_dialactions[event] = dialaction

            self.group_dialactions[event].action = dialaction.action
            self.group_dialactions[event].actionarg1 = dialaction.actionarg1
            self.group_dialactions[event].actionarg2 = dialaction.actionarg2

    @property
    def members(self):
        return self

    def fix_extension(self):
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
