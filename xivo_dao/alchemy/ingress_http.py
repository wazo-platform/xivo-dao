# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, text
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import String, Text

from xivo_dao.helpers.db_manager import Base


class IngressHTTP(Base):

    __tablename__ = 'ingress_http'

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True)
    uri = Column(Text, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        unique=True,
        nullable=False,
    )
