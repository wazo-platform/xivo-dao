# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    PrimaryKeyConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.sql import (
    cast,
    select,
)
from sqlalchemy.types import (
    Integer,
    String,
    Text,
)

from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers.db_manager import Base


class Incall(Base):

    __tablename__ = 'incall'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('exten', 'context'),
        Index('incall__idx__context', 'context'),
        Index('incall__idx__exten', 'exten'),
    )

    id = Column(Integer)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    exten = Column(String(40))
    context = Column(String(39))
    preprocess_subroutine = Column(String(39))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    caller_id = relationship(
        'Callerid',
        primaryjoin="""and_(Callerid.type == 'incall',
                            Callerid.typeval == Incall.id)""",
        foreign_keys='Callerid.typeval',
        cascade='all, delete-orphan',
        uselist=False,
    )

    caller_id_mode = association_proxy(
        'caller_id',
        'mode',
        creator=lambda _mode: Callerid(type='incall', mode=_mode),
    )
    caller_id_name = association_proxy(
        'caller_id',
        'name',
        creator=lambda _name: Callerid(type='incall', name=_name),
    )

    dialaction = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.category == 'incall',
                            Dialaction.categoryval == cast(Incall.id, String))""",
        foreign_keys='Dialaction.categoryval',
        cascade='all, delete-orphan',
        uselist=False,
        back_populates='incall',
    )

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'incall',
                            Extension.typeval == cast(Incall.id, String))""",
        foreign_keys='Extension.typeval',
        viewonly=True,
        back_populates='incall',
    )

    schedule_paths = relationship(
        'SchedulePath',
        primaryjoin="""and_(SchedulePath.path == 'incall',
                            SchedulePath.pathid == Incall.id)""",
        foreign_keys='SchedulePath.pathid',
        cascade='all, delete-orphan',
        back_populates='incall',
    )

    schedules = association_proxy(
        'schedule_paths',
        'schedule',
        creator=lambda _schedule: SchedulePath(
            path='incall',
            schedule_id=_schedule.id,
            schedule=_schedule,
        ),
    )

    @property
    def destination(self):
        return self.dialaction

    @destination.setter
    def destination(self, destination):
        if not self.dialaction:
            destination.event = 'answer'
            destination.category = 'incall'
            destination.linked = 1
            self.dialaction = destination

        self.dialaction.action = destination.action
        self.dialaction.actionarg1 = destination.actionarg1
        self.dialaction.actionarg2 = destination.actionarg2

    @hybrid_property
    def user_id(self):
        if self.dialaction and self.dialaction.action == 'user':
            return int(self.dialaction.actionarg1)
        return None

    @user_id.expression
    def user_id(cls):
        return (select([cast(Dialaction.actionarg1, Integer)])
                .where(Dialaction.action == 'user')
                .where(Dialaction.category == 'incall')
                .where(Dialaction.categoryval == cast(cls.id, String))
                .as_scalar())
