# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class LdapFilter(Base):

    __tablename__ = 'ldapfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    ldapserverid = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False, server_default='')
    user = Column(String(255))
    passwd = Column(String(255))
    basedn = Column(String(255), nullable=False, server_default='')
    filter = Column(String(255), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, default='')
