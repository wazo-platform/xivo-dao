# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.types import Integer, String, Text
from sqlalchemy.schema import Column, UniqueConstraint

from xivo_dao.helpers.db_manager import Base


class LineFeatures(Base):

    __tablename__ = 'linefeatures'
    __table_args__ = (
        UniqueConstraint('name'),
        UniqueConstraint('protocol', 'protocolid'),
    )

    id = Column(Integer, primary_key=True)
    protocolid = Column(Integer, nullable=False)
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128), nullable=False)
    number = Column(String(40))
    context = Column(String(39), nullable=False)
    provisioningid = Column(Integer, nullable=False)
    num = Column(Integer, server_default='0')
    ipfrom = Column(String(15))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    protocol = Column(String(10))
