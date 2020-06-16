# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.ext.associationproxy import association_proxy
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
        passive_deletes=True,
    )

    options = association_proxy(
        '_options', 'option',
        creator=lambda _option: EndpointSIPSectionOption(key=_option[0], value=_option[1]),
    )

    def find(self, term):
        return [
            (option.key, option.value) for option in self._options if option.key == term
        ]

    def add_or_replace(self, option_name, value):
        for option in self._options:
            if option.key == option_name:
                option.value = value
                return

        self._options.append(EndpointSIPSectionOption(key=option_name, value=value))
