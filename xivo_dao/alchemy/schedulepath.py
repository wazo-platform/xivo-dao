# -*- coding: utf-8 -*-

# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
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

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class SchedulePath(Base):

    __tablename__ = 'schedule_path'
    __table_args__ = (
        PrimaryKeyConstraint('schedule_id', 'path', 'pathid'),
        Index('schedule_path_path', 'path', 'pathid'),
    )

    schedule_id = Column(Integer, ForeignKey('schedule.id'))
    path = Column(enum.schedule_path_type, nullable=False)
    pathid = Column(Integer, autoincrement=False)

    incall = relationship('Incall',
                          primaryjoin="""and_(SchedulePath.path == 'incall',
                                              SchedulePath.pathid == Incall.id)""",
                          foreign_keys='SchedulePath.pathid',
                          viewonly=True,
                          back_populates='schedule_paths')

    schedule = relationship('Schedule',
                            back_populates='schedule_paths')
