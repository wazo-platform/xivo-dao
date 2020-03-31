# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Table, text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, Text, Boolean

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip_section import EndpointSIPSection


parent_child = Table(
    'endpoint_sip_parent',
    Base.metadata,
    Column(
        'child_uuid',
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'parent_uuid',
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='CASCADE'),
        primary_key=True,
    )
)


class EndpointSIP(Base):

    __tablename__ = 'endpoint_sip'
    __table_args__ = (UniqueConstraint('name'),)

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True)
    display_name = Column(Text, nullable=False)  # For the UI (select boxes etc)
    name = Column(
        Text,
        server_default=text('substring(md5(random()::text), 0, 9)'),  # Generates a random name
        nullable=False,
    )
    asterisk_id = Column(Text)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    aor_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    auth_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    endpoint_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    identify_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    registration_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    registration_outbound_auth_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    outbound_auth_section_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip_section.uuid'))
    transport_uuid = Column(UUID(as_uuid=True), ForeignKey('pjsip_transport.uuid'), nullable=True)
    template = Column(Boolean, server_default=text('false'))

    transport = relationship('PJSIPTransport')
    parents = relationship(
        'EndpointSIP',
        primaryjoin='EndpointSIP.uuid==endpoint_sip_parent.c.child_uuid',
        secondaryjoin='EndpointSIP.uuid==endpoint_sip_parent.c.parent_uuid',
        secondary=parent_child,
    )

    _aor_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.aor_section_uuid',
    )
    _auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.auth_section_uuid',
    )
    _endpoint_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.endpoint_section_uuid',
    )
    _registration_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.registration_section_uuid',
    )
    _registration_outbound_auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.registration_outbound_auth_section_uuid',
    )
    _identify_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.identify_section_uuid',
    )
    _outbound_auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.outbound_auth_section_uuid',
    )

    def __init__(
        self,
        *args,
        aor_section_options=None,
        auth_section_options=None,
        endpoint_section_options=None,
        registration_section_options=None,
        registration_outbound_auth_section_options=None,
        identify_section_options=None,
        outbound_auth_section_options=None,
        **kwargs
    ):
        if aor_section_options:
            kwargs['_aor_section'] = EndpointSIPSection(options=aor_section_options)
        if auth_section_options:
            kwargs['_auth_section'] = EndpointSIPSection(options=auth_section_options)
        if endpoint_section_options:
            kwargs['_endpoint_section'] = EndpointSIPSection(options=endpoint_section_options)
        if registration_section_options:
            kwargs['_registration_section'] = EndpointSIPSection(options=registration_section_options)
        if registration_outbound_auth_section_options:
            kwargs['_registration_outbound_auth_section'] = EndpointSIPSection(options=registration_outbound_auth_section_options)
        if endpoint_section_options:
            kwargs['_identify_section'] = EndpointSIPSection(options=identify_section_options)
        if endpoint_section_options:
            kwargs['_outbound_auth_section'] = EndpointSIPSection(options=outbound_auth_section_options)
        super(EndpointSIP, self).__init__(*args, **kwargs)

    def __str__(self):
        klass = self.__class__.__name__
        return f'{klass}(uuid={self.uuid}, name={self.name}, aor_section_uuid={self.aor_section_uuid}, auth_section_uuid={self.auth_section_uuid})'

    @property
    def aor_section_options(self):
        return self._get_section_options(self._aor_section)

    @property
    def auth_section_options(self):
        return self._get_section_options(self._auth_section)

    @property
    def endpoint_section_options(self):
        return self._get_section_options(self._endpoint_section)

    @property
    def registration_section_options(self):
        return self._get_section_options(self._registration_section)

    @property
    def registration_outbound_auth_section_options(self):
        return self._get_section_options(self._registration_outbound_auth_section)

    @property
    def identify_section_options(self):
        return self._get_section_options(self._identify_section)

    @property
    def outbound_auth_section_options(self):
        return self._get_section_options(self._outbound_auth_section)

    def _get_section_options(self, section):
        if not section:
            return []

        return [[option.key, option.value] for option in section.options]
