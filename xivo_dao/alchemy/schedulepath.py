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

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class SchedulePath(Base):

    __tablename__ = 'schedule_path'
    __table_args__ = (
        PrimaryKeyConstraint('schedule_id', 'path', 'pathid'),
    )

    schedule_id = Column(Integer, autoincrement=False)
    path = Column(String(9), autoincrement=False)
    pathid = Column(Integer, autoincrement=False)
    order = Column(Integer, nullable=False)
