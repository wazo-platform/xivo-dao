# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Text

from xivo_dao.helpers.db_manager import Base

from .pjsip_transport_option import PJSIPTransportOption


class PJSIPTransport(Base):
    __tablename__ = 'pjsip_transport'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('name'),
    )

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    name = Column(Text, nullable=False)
    _options = relationship(
        'PJSIPTransportOption',
        cascade='all, delete-orphan',
        passive_deletes=True,
        passive_updates=False,
    )

    def __init__(self, **kwargs):
        options = kwargs.pop('options', [])
        super().__init__(**kwargs)
        for key, value in options:
            self._options.append(PJSIPTransportOption(key=key, value=value))

    @property
    def options(self):
        return [[option.key, option.value] for option in self._options]

    @options.setter
    def options(self, options):
        remaining_options = list(options)
        new_options = []

        for option in self._options:
            if (option.key, option.value) not in remaining_options:
                continue
            new_options.append(option)
            remaining_options.remove((options.key, options.value))

        for key, value in remaining_options:
            new_options.append(PJSIPTransportOption(key=key, value=value))

        self._options = new_options
