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

# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
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

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.types import Integer, String, Text, Enum
from sqlalchemy.schema import Column


class LineFeatures(Base):

    __tablename__ = 'linefeatures'

    id = Column(Integer, primary_key=True)
    protocolid = Column(Integer, nullable=False)
    iduserfeatures = Column(Integer, default=0)
    config = Column(String(128))
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128), nullable=False)
    number = Column(String(40))
    context = Column(String(39), nullable=False)
    provisioningid = Column(Integer, nullable=False)
    rules_type = Column(String(16))
    rules_time = Column(String(8))
    rules_order = Column(Integer, default=0)
    rules_group = Column(String(16))
    num = Column(Integer, default=0)
    line_num = Column(Integer, default=0)
    ipfrom = Column(String(15))
    internal = Column(Integer, nullable=False, default=0)
    commented = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    protocol = Column(String(10))
