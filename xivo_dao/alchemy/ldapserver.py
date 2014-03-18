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

from xivo_dao.helpers.db_manager import Base, Type
from sqlalchemy.schema import Column, Sequence
from sqlalchemy.types import Integer, String, Text, Enum


class LdapServer(Base):

    __tablename__ = 'ldapserver'

    id = Column(Integer, Sequence('ldapserver_id_seq'), primary_key=True)
    name = Column(String(128), nullable=False, server_default='')
    host = Column(String(255), nullable=False, server_default='')
    port = Column(Integer, nullable=False)
    securitylayer = Column(Enum('tls',
                                'ssl',
                                name='ldapserver_securitylayer',
                                metadata=Type.metadata))
    protocolversion = Column(Enum('2',
                                  '3',
                                  name='ldapserver_protocolversion',
                                  metadata=Type.metadata),
                             nullable=False,
                             default='3')
    disable = Column(Integer, nullable=False, default=0)
    dcreate = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=False)
