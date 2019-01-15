# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from sqlalchemy import text
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import String
from xivo_dao.helpers.db_manager import Base


class Tenant(Base):

    __tablename__ = 'tenant'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(36), server_default=text('uuid_generate_v4()'))
