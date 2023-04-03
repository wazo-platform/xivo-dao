# Copyright 2007-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Integer, String, Text, Boolean

from xivo import dialaction
from xivo_dao.helpers.db_manager import Base, IntAsString

from . import enum


class Schedule(Base):

    __tablename__ = 'schedule'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('schedule__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(255))
    timezone = Column(String(128))
    fallback_action = Column(enum.dialaction_action, nullable=False, server_default='none')
    fallback_actionid = Column(IntAsString(255))
    fallback_actionargs = Column(String(255))
    description = Column(Text)
    commented = Column(Integer, nullable=False, server_default='0')

    periods = relationship(
        'ScheduleTime',
        primaryjoin='ScheduleTime.schedule_id == Schedule.id',
        foreign_keys='ScheduleTime.schedule_id',
        cascade='all, delete-orphan',
    )

    schedule_paths = relationship('SchedulePath', cascade='all, delete-orphan')

    schedule_incalls = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.schedule_id == Schedule.id,
            SchedulePath.path == 'incall'
        )""",
        viewonly=True,
    )
    incalls = association_proxy('schedule_incalls', 'incall')

    schedule_users = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.schedule_id == Schedule.id,
            SchedulePath.path == 'user'
        )""",
        viewonly=True,
    )
    users = association_proxy('schedule_users', 'user')

    schedule_groups = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.schedule_id == Schedule.id,
            SchedulePath.path == 'group'
        )""",
        viewonly=True,
    )
    groups = association_proxy('schedule_groups', 'group')

    schedule_outcalls = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.schedule_id == Schedule.id,
            SchedulePath.path == 'outcall'
        )""",
        viewonly=True,
    )
    outcalls = association_proxy('schedule_outcalls', 'outcall')

    schedule_queues = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.schedule_id == Schedule.id,
            SchedulePath.path == 'queue'
        )""",
        viewonly=True,
    )
    queues = association_proxy('schedule_queues', 'queue')

    @property
    def open_periods(self):
        return self._get_periods('opened')

    @open_periods.setter
    def open_periods(self, value):
        self._set_periods('opened', value)

    @property
    def exceptional_periods(self):
        return self._get_periods('closed')

    @exceptional_periods.setter
    def exceptional_periods(self, value):
        self._set_periods('closed', value)

    def _get_periods(self, mode):
        return [period for period in self.periods if period.mode == mode]

    def _set_periods(self, mode, periods):
        self.periods = [period for period in self.periods if period.mode != mode]
        for period in periods:
            period.mode = mode
            self.periods.append(period)

    @property
    def closed_destination(self):
        return self

    @property
    def type(self):
        return dialaction.action_type(self.fallback_action)

    @type.setter
    def type(self, value):
        self.fallback_action = dialaction.action(type_=value, subtype=self.subtype)

    @property
    def subtype(self):
        return dialaction.action_subtype(self.fallback_action)

    @subtype.setter
    def subtype(self, value):
        self.fallback_action = dialaction.action(type_=self.type, subtype=value)

    @hybrid_property
    def actionarg1(self):
        if self.fallback_actionid == '':
            return None
        return self.fallback_actionid

    @actionarg1.setter
    def actionarg1(self, value):
        self.fallback_actionid = value

    @hybrid_property
    def actionarg2(self):
        if self.fallback_actionargs == '':
            return None
        return self.fallback_actionargs

    @actionarg2.setter
    def actionarg2(self, value):
        self.fallback_actionargs = value

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)
