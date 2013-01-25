# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO dao is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO dao
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


class DeviceFeatures(Base):
    __tablename__ = 'devicefeatures'

    id = Column(Integer, primary_key=True)
    deviceid = Column(String(32), nullable=False)
    commented = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    config = Column(String(32))
    plugin = Column(String(64))
    ip = Column(String(39))
    mac = Column(String(17), nullable=False)
    sn = Column(String(64))
    vendor = Column(String(32), nullable=False)
    model = Column(String(32), nullable=False)
    version = Column(String(32))
    proto = Column(String(16), nullable=False)
    internal = Column(Integer, nullable=False, default=0)
    configured = Column(Integer, nullable=False, default=0)
