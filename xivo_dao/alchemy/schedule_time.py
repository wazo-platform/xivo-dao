# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum

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
    mode = Column(Enum('opened', 'closed',
                       name='schedule_time_mode',
                       metadata=Base.metadata),
                  nullable=False, server_default='opened')
    hours = Column(String(512))
    weekdays = Column(String(512))
    monthdays = Column(String(512))
    months = Column(String(512))
    action = Column(enum.dialaction_action)
    actionid = Column(IntAsString(255))
    actionargs = Column(String(255))
    commented = Column(Integer, nullable=False, server_default='0')

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
        self.hours = '{}{}'.format(hours_start,
                                   '-{}'.format(hours_end) if hours_end else '')

    @property
    def week_days(self):
        if not self.weekdays:
            return [1, 2, 3, 4, 5, 6, 7]
        return self._expand_range(self.weekdays)

    @week_days.setter
    def week_days(self, value):
        self.weekdays = self._convert_array_to_str(value)

    @property
    def month_days(self):
        if not self.monthdays:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9,
                    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                    30, 31]
        return self._expand_range(self.monthdays)

    @month_days.setter
    def month_days(self, value):
        self.monthdays = self._convert_array_to_str(value)

    @property
    def months_list(self):
        if not self.months:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
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
        return self.action.split(':', 1)[0] if self.action else self.action

    @type.setter
    def type(self, value):
        type_ = value if value else ''
        subtype = self.subtype if self.subtype else ''
        self._set_action(type_, subtype)

    @property
    def subtype(self):
        type_subtype = self.action.split(':', 1) if self.action else ''
        return type_subtype[1] if len(type_subtype) == 2 else None

    @subtype.setter
    def subtype(self, value):
        type_ = self.type if self.type else ''
        subtype = value if value else ''
        self._set_action(type_, subtype)

    def _set_action(self, type_, subtype):
        subtype = ':{}'.format(subtype) if subtype else ''
        self.action = '{}{}'.format(type_, subtype)

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
