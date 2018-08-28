# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import (
    Column,
    ForeignKey,
)
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class Application(Base):

    __tablename__ = 'application'

    uuid = Column(String(36), primary_key=True, server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    name = Column(String(128))

    dest_node = relationship(
        'ApplicationDestNode',
        passive_deletes=True,
        uselist=False,
    )
