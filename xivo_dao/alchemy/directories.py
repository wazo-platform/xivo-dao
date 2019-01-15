# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .ldapfilter import LdapFilter


class Directories(Base):

    __tablename__ = 'directories'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    uri = Column(String(255))
    dirtype = Column(String(20), nullable=False)
    name = Column(String(255))
    description = Column(Text, nullable=False, default='')
    xivo_username = Column(Text)
    xivo_password = Column(Text)
    auth_key_file = Column(Text)
    xivo_verify_certificate = Column(Boolean, nullable=False, server_default='False')
    xivo_custom_ca_path = Column(Text)
    dird_tenant = Column(Text)
    dird_phonebook = Column(Text)
    auth_host = Column(Text)
    auth_port = Column(Integer)
    auth_backend = Column(Text)
    auth_verify_certificate = Column(Boolean, nullable=False, server_default='False')
    auth_custom_ca_path = Column(Text)
    ldapfilter_id = Column(Integer, ForeignKey(LdapFilter.id, ondelete='CASCADE'), nullable=True)
