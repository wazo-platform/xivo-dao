# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Text

from xivo_dao.helpers.db_manager import Base


class EndpointSIPSectionOption(Base):
    __tablename__ = 'endpoint_sip_section_option'

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    endpoint_sip_section_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip_section.uuid'),
        nullable=False,
    )
