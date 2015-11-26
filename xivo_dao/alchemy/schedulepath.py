# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum
from xivo_dao.alchemy.schedule import Schedule


class SchedulePath(Base):

    __tablename__ = 'schedule_path'
    __table_args__ = (
        PrimaryKeyConstraint('schedule_id', 'path', 'pathid'),
        Index('schedule_path_path', 'path', 'pathid'),
    )

    schedule_id = Column(Integer, autoincrement=False)
    path = Column(enum.schedule_path_type, nullable=False, autoincrement=False)
    pathid = Column(Integer, autoincrement=False)
    order = Column(Integer, nullable=False)

    schedule = relationship(Schedule,
                            foreign_keys=schedule_id,
                            primaryjoin=(Schedule.id == schedule_id))
