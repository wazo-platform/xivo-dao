# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text


class QueueSkill(Base):

    __tablename__ = 'queueskill'

    id = Column(Integer, primary_key=True, nullable=False)
    catid = Column(Integer, default=1, nullable=False)
    name = Column(String(64), default='', nullable=False)
    description = Column(Text, nullable=False)
    printscreen = Column(String(5))
