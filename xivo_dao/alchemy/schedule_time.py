# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum

from xivo import dialaction
from xivo_dao.helpers.db_manager import Base, IntAsString
from xivo_dao.alchemy import enum


class ScheduleTime(Base):
    __tablename__ = 'schedule_time'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('schedule_time__idx__scheduleid_commented', 'schedule_id', 'commented'),
    )

    id = Column(Integer)
    schedule_id = Column(Integer)
    mode = Column(
        Enum('opened', 'closed', name='schedule_time_mode', metadata=Base.metadata),
        nullable=False,
        server_default='opened',
    )
    hours = Column(String(512))
    weekdays = Column(String(512))
    monthdays = Column(String(512))
    months = Column(String(512))
    action = Column(enum.dialaction_action)
    actionid = Column(IntAsString(255))
    actionargs = Column(String(255))
    commented = Column(Integer, nullable=False, server_default='0')

    conference = relationship(
        'Conference',
        primaryjoin="""and_(
            ScheduleTime.action == 'conference',
            ScheduleTime.actionid == cast(Conference.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    group = relationship(
        'GroupFeatures',
        primaryjoin="""and_(
            ScheduleTime.action == 'group',
            ScheduleTime.actionid == cast(GroupFeatures.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    user = relationship(
        'UserFeatures',
        primaryjoin="""and_(
            ScheduleTime.action == 'user',
            ScheduleTime.actionid == cast(UserFeatures.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    ivr = relationship(
        'IVR',
        primaryjoin="""and_(
            ScheduleTime.action == 'ivr',
            ScheduleTime.actionid == cast(IVR.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    switchboard = relationship(
        'Switchboard',
        primaryjoin="""and_(
            ScheduleTime.action == 'switchboard',
            ScheduleTime.actionid == Switchboard.uuid
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    voicemail = relationship(
        'Voicemail',
        primaryjoin="""and_(
            ScheduleTime.action == 'voicemail',
            ScheduleTime.actionid == cast(Voicemail.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    application = relationship(
        'Application',
        primaryjoin="""and_(
            ScheduleTime.action == 'application:custom',
            ScheduleTime.actionid == Application.uuid
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    queue = relationship(
        'QueueFeatures',
        primaryjoin="""and_(
            ScheduleTime.action == 'queue',
            ScheduleTime.actionid == cast(QueueFeatures.id, String)
        )""",
        foreign_keys='ScheduleTime.actionid',
        viewonly=True,
    )

    @property
    def destination(self):
        return self

    @property
    def hours_start(self):
        return self.hours.split('-', 1)[0] if self.hours else None

    @hours_start.setter
    def hours_start(self, value):
        hours_start = value if value else ''
        hours_end = self.hours_end if self.hours_end else ''
        self._set_hours(hours_start, hours_end)

    @property
    def hours_end(self):
        hours = self.hours.split('-', 1) if self.hours else ''
        return hours[1] if len(hours) == 2 else None

    @hours_end.setter
    def hours_end(self, value):
        hours_start = self.hours_start if self.hours_start else ''
        hours_end = value if value else ''
        self._set_hours(hours_start, hours_end)

    def _set_hours(self, hours_start, hours_end):
        end_suffix = f'-{hours_end}' if hours_end else ''
        self.hours = f'{hours_start}{end_suffix}'

    @property
    def week_days(self):
        if not self.weekdays:
            return list(range(1, 8))
        return self._expand_range(self.weekdays)

    @week_days.setter
    def week_days(self, value):
        self.weekdays = self._convert_array_to_str(value)

    @property
    def month_days(self):
        if not self.monthdays:
            return list(range(1, 32))
        return self._expand_range(self.monthdays)

    @month_days.setter
    def month_days(self, value):
        self.monthdays = self._convert_array_to_str(value)

    @property
    def months_list(self):
        if not self.months:
            return list(range(1, 13))
        return self._expand_range(self.months)

    @months_list.setter
    def months_list(self, value):
        self.months = self._convert_array_to_str(value)

    def _expand_range(self, multi_range):
        if not multi_range:
            return multi_range

        result = []
        for item in multi_range.split(','):
            if '-' in item:
                start, end = map(int, item.split('-', 2))
                result += list(range(start, end + 1))
            else:
                result.append(int(item))
        return result

    def _convert_array_to_str(self, value):
        return ','.join(str(x) for x in value) if value else value

    @property
    def type(self):
        return dialaction.action_type(self.action)

    @type.setter
    def type(self, value):
        self.action = dialaction.action(type_=value, subtype=self.subtype)

    @property
    def subtype(self):
        return dialaction.action_subtype(self.action)

    @subtype.setter
    def subtype(self, value):
        self.action = dialaction.action(type_=self.type, subtype=value)

    @hybrid_property
    def actionarg1(self):
        return self.actionid

    @actionarg1.setter
    def actionarg1(self, value):
        self.actionid = value

    @hybrid_property
    def actionarg2(self):
        return self.actionargs

    @actionarg2.setter
    def actionarg2(self, value):
        self.actionargs = value
