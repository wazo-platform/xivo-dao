# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
