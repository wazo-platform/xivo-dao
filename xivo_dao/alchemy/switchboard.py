# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import String
from sqlalchemy.sql.schema import ForeignKey

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.helpers.uuid import new_uuid


class Switchboard(Base):

    __tablename__ = 'switchboard'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    name = Column(String(128), nullable=False)
    hold_moh_uuid = Column(String(38), ForeignKey('moh.uuid', ondelete='SET NULL'))
    queue_moh_uuid = Column(String(38), ForeignKey('moh.uuid', ondelete='SET NULL'))

    incall_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.category == 'incall',
            Dialaction.action == 'switchboard',
            Dialaction.actionarg1 == Switchboard.uuid
        )""",
        foreign_keys='Dialaction.actionarg1',
        viewonly=True
    )

    incalls = association_proxy('incall_dialactions', 'incall')

    switchboard_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.action == 'switchboard',
                            Dialaction.categoryval == Switchboard.uuid)""",
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('event'),
        foreign_keys='Dialaction.categoryval',
    )

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.action == 'switchboard',
            Dialaction.actionarg1 == Switchboard.uuid
        )""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
    )

    switchboard_member_users = relationship(
        'SwitchboardMemberUser',
        primaryjoin="""SwitchboardMemberUser.switchboard_uuid == Switchboard.uuid""",
        cascade='all, delete-orphan',
    )

    user_members = association_proxy(
        'switchboard_member_users', 'user',
        creator=lambda _user: SwitchboardMemberUser(user=_user),
    )

    _queue_moh = relationship('MOH', primaryjoin='Switchboard.queue_moh_uuid == MOH.uuid')
    _hold_moh = relationship('MOH', primaryjoin='Switchboard.hold_moh_uuid == MOH.uuid')

    @property
    def queue_music_on_hold(self):
        return self._queue_moh.name if self._queue_moh else None

    @property
    def waiting_room_music_on_hold(self):
        return self._hold_moh.name if self._hold_moh else None

    @property
    def fallbacks(self):
        return self.switchboard_dialactions

    # Note: fallbacks[key] = Dialaction() doesn't pass in this method
    @fallbacks.setter
    def fallbacks(self, dialactions):
        for event in list(self.switchboard_dialactions.keys()):
            if event not in dialactions:
                self.switchboard_dialactions.pop(event, None)

        for event, dialaction in six.iteritems(dialactions):
            self._set_dialaction(event, dialaction)

    def _set_dialaction(self, event, dialaction):
        if dialaction is None:
            self.switchboard_dialactions.pop(event, None)
            return

        if event not in self.switchboard_dialactions:
            dialaction.event = event
            dialaction.category = 'incall'
            self.switchboard_dialactions[event] = dialaction

        self.switchboard_dialactions[event].action = dialaction.action
        self.switchboard_dialactions[event].actionarg1 = dialaction.actionarg1
        self.switchboard_dialactions[event].actionarg2 = dialaction.actionarg2
