# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text


class Voicemenu(Base):

    __tablename__ = 'voicemenu'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(29), nullable=False, default='')
    number = Column(String(40), nullable=False)
    context = Column(String(39), nullable=False)
    commented = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=False)
