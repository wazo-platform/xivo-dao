# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Enum, text, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip_section_option import EndpointSIPSectionOption


class EndpointSIPSection(Base):
    __tablename__ = 'endpoint_sip_section'
    __table_args__ = (
        UniqueConstraint('type', 'endpoint_sip_uuid'),
        Index('endpoint_sip_section__idx__endpoint_sip_uuid', 'endpoint_sip_uuid'),
    )

    uuid = Column(
        UUID(as_uuid=True),
        server_default=text('uuid_generate_v4()'),
        primary_key=True,
    )
    type = Column(
        'type',
        Enum(
            'aor',
            'auth',
            'endpoint',
            'identify',
            'outbound_auth',
            'registration_outbound_auth',
            'registration',
            name='endpoint_sip_section_type',
        ),
        nullable=False,
    )
    endpoint_sip_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='CASCADE'),
        nullable=False,
    )

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'section'}

    _options = relationship(
        'EndpointSIPSectionOption',
        cascade='all, delete-orphan',
        passive_deletes=True,
        lazy='joined',
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


class AORSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'aor'}


class AuthSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'auth'}


class EndpointSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'endpoint'}


class IdentifySection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'identify'}


class OutboundAuthSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'outbound_auth'}


class RegistrationOutboundAuthSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'registration_outbound_auth'}


class RegistrationSection(EndpointSIPSection):

    __mapper_args__ = {'polymorphic_identity': 'registration'}
