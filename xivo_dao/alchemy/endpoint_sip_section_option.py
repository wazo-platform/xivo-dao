# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import Text

from xivo_dao.helpers.db_manager import Base


class EndpointSIPSectionOption(Base):
    __tablename__ = 'endpoint_sip_section_option'
    __table_args__ = (
        Index(
            'endpoint_sip_section_option__idx__endpoint_sip_section_uuid',
            'endpoint_sip_section_uuid',
        ),
    )

    uuid = Column(
        UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True
    )
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    endpoint_sip_section_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip_section.uuid', ondelete='CASCADE'),
        nullable=False,
    )

    @property
    def option(self):
        return [self.key, self.value]

    @option.setter
    def option(self, option):
        self.key, self.value = option
