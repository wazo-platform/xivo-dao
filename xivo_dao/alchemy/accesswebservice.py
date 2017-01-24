# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

import uuid

from sqlalchemy.schema import Column, UniqueConstraint, Index
from sqlalchemy.types import Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from xivo_dao.helpers.db_manager import Base


def _new_uuid():
    return str(uuid.uuid4())


class AccessWebService(Base):

    __tablename__ = 'accesswebservice'
    __table_args__ = (
        UniqueConstraint('name'),
        UniqueConstraint('uuid'),
        Index('accesswebservice__idx__disable', 'disable'),
        Index('accesswebservice__idx__host', 'host'),
        Index('accesswebservice__idx__login', 'login'),
        Index('accesswebservice__idx__passwd', 'passwd')
    )

    id = Column(Integer, primary_key=True)
    uuid = Column(String(38), nullable=False, default=_new_uuid, server_default='uuid_generate_v4()')
    name = Column(String(64), nullable=False, server_default='')
    login = Column(String(64))
    passwd = Column(String(64))
    host = Column(String(255))
    acl = Column(ARRAY(String), nullable=False, server_default='{}')
    disable = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, server_default='')
