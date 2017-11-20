# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import uuid

from sqlalchemy import text
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
    uuid = Column(String(38), nullable=False, default=_new_uuid, server_default=text('uuid_generate_v4()'))
    name = Column(String(64), nullable=False, server_default='')
    login = Column(String(64))
    passwd = Column(String(64))
    host = Column(String(255))
    acl = Column(ARRAY(String), nullable=False, server_default='{}')
    disable = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, server_default='')
