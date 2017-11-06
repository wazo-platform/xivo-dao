# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.helpers.db_manager import Base


class IVR(Base):

    __tablename__ = 'ivr'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    greeting_sound = Column(Text)
    menu_sound = Column(Text, nullable=False)
    invalid_sound = Column(Text)
    abort_sound = Column(Text)
    timeout = Column(Integer, nullable=False, server_default='5')
    max_tries = Column(Integer, nullable=False, server_default='3')
    description = Column(Text)

    dialactions = relationship(Dialaction,
                               primaryjoin="""and_(Dialaction.category == 'ivr',
                                                   Dialaction.categoryval == cast(IVR.id, String))""",
                               foreign_keys='Dialaction.categoryval',
                               collection_class=attribute_mapped_collection('event'),
                               cascade='all, delete-orphan')

    choices = relationship(IVRChoice,
                           cascade='all, delete-orphan')

    incall_dialactions = relationship('Dialaction',
                                      primaryjoin="""and_(Dialaction.category == 'incall',
                                                          Dialaction.action == 'ivr',
                                                          Dialaction.actionarg1 == cast(IVR.id, String))""",
                                      foreign_keys='Dialaction.actionarg1',
                                      viewonly=True)

    incalls = association_proxy('incall_dialactions', 'incall')

    ivr_dialactions = relationship('Dialaction',
                                   primaryjoin="""and_(Dialaction.action == 'ivr',
                                                       Dialaction.actionarg1 == cast(IVR.id, String),
                                                       Dialaction.category.in_(['ivr', 'ivr_choice']))""",
                                   foreign_keys='Dialaction.actionarg1',
                                   cascade='all, delete-orphan')

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
            dialaction.linked = 1
            self.dialactions[event] = dialaction

        self.dialactions[event].action = dialaction.action
        self.dialactions[event].actionarg1 = dialaction.actionarg1
        self.dialactions[event].actionarg2 = dialaction.actionarg2
