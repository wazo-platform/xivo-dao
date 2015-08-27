# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class LdapServer(Base):

    __tablename__ = 'ldapserver'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        UniqueConstraint('host', 'port'),
    )

    id = Column(Integer)
    name = Column(String(64), nullable=False, server_default='')
    host = Column(String(255), nullable=False, server_default='')
    port = Column(Integer, nullable=False)
    securitylayer = Column(enum.ldapserver_securitylayer)
    protocolversion = Column(enum.ldapserver_protocolversion, nullable=False, server_default='3')
    disable = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, default='')
