# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.ext.hybrid import hybrid_property
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

    def __init__(self, *args, options=None, **kwargs):
        super(EndpointSIPSection, self).__init__(*args, **kwargs)
        if options:
            for key, value in options:
                self._options.append(EndpointSIPSectionOption(key=key, value=value))

    @hybrid_property
    def options(self):
        return [[option.key, option.value] for option in self._options]

    @options.setter
    def options(self, value):
        original_length = len(self._options)
        new_length = len(value)

        for i, (key, value) in enumerate(value):
            if i < original_length:
                matching_option = self._options[i]
                if matching_option.key == key and matching_option.value == value:
                    continue
                else:
                    matching_option.key = key
                    matching_option.value = value
            else:
                self._options.append(EndpointSIPSectionOption(key=key, value=value))

        if original_length > new_length:
            self._options = self._options[:new_length]

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
