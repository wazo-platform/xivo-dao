# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import UUID

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip_section_option import EndpointSIPSectionOption


class EndpointSIPSection(Base):
    __tablename__ = 'endpoint_sip_section'

    uuid = Column(
        UUID(as_uuid=True),
        server_default=text('uuid_generate_v4()'),
        primary_key=True,
    )

    _options = relationship(
        'EndpointSIPSectionOption',
        cascade='all, delete-orphan',
    )

    def __init__(self, *args, options=None, **kwargs):
        super(EndpointSIPSection, self).__init__(*args, **kwargs)
        if options:
            for key, value in options:
                self._options.append(EndpointSIPSectionOption(key=key, value=value))

    @property
    def options(self):
        return self._options
