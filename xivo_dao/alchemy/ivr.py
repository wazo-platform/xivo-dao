# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.helpers.db_manager import Base


class IVR(Base):
    __tablename__ = 'ivr'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('ivr__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    name = Column(String(128), nullable=False)
    greeting_sound = Column(Text)
    menu_sound = Column(Text, nullable=False)
    invalid_sound = Column(Text)
    abort_sound = Column(Text)
    timeout = Column(Integer, nullable=False, server_default='5')
    max_tries = Column(Integer, nullable=False, server_default='3')
    description = Column(Text)

    dialactions = relationship(
        Dialaction,
        primaryjoin="""and_(
            Dialaction.category == 'ivr',
            Dialaction.categoryval == cast(IVR.id, String)
        )""",
        foreign_keys='Dialaction.categoryval',
        collection_class=attribute_mapped_collection('event'),
        cascade='all, delete-orphan',
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'group_dialactions,'
            'ivr_choice,'
            'queue_dialactions,'
            'switchboard_dialactions,'
            'user_dialactions,'
        ),
    )

    choices = relationship(
        IVRChoice,
        cascade='all, delete-orphan',
    )

    incall_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.category == 'incall',
            Dialaction.action == 'ivr',
            Dialaction.actionarg1 == cast(IVR.id, String)
        )""",
        foreign_keys='Dialaction.actionarg1',
        viewonly=True,
    )

    incalls = association_proxy('incall_dialactions', 'incall')

    _dialaction_actions = relationship(
        Dialaction,
        primaryjoin="""and_(
            Dialaction.action == 'ivr',
            Dialaction.actionarg1 == cast(IVR.id, String),
        )""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
        overlaps='_dialaction_actions',
    )

    @property
    def invalid_destination(self):
        return self.dialactions.get('invalid')

    @invalid_destination.setter
    def invalid_destination(self, destination):
        self._set_dialaction('invalid', destination)

    @property
    def timeout_destination(self):
        return self.dialactions.get('timeout')

    @timeout_destination.setter
    def timeout_destination(self, destination):
        self._set_dialaction('timeout', destination)

    @property
    def abort_destination(self):
        return self.dialactions.get('abort')

    @abort_destination.setter
    def abort_destination(self, destination):
        self._set_dialaction('abort', destination)

    def _set_dialaction(self, event, dialaction):
        if dialaction is None:
            self.dialactions.pop(event, None)
            return

        if event not in self.dialactions:
            dialaction.event = event
            dialaction.category = 'ivr'
            self.dialactions[event] = dialaction

        self.dialactions[event].action = dialaction.action
        self.dialactions[event].actionarg1 = dialaction.actionarg1
        self.dialactions[event].actionarg2 = dialaction.actionarg2
