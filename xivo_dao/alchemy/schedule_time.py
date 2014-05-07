# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base
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
    actionid = Column(String(512))
    actionargs = Column(String(512))
    commented = Column(Integer, nullable=False, server_default='0')
