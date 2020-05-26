# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from sqlalchemy import and_, Table, text, Integer, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, Text, Boolean

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip_section import EndpointSIPSection
from .endpoint_sip_section_option import EndpointSIPSectionOption

logger = logging.getLogger(__name__)


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
    display_name = Column(Text)  # For the UI (select boxes etc)
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
    context_id = Column(Integer, ForeignKey('context.id'), nullable=True)
    template = Column(Boolean, server_default=text('false'))

    transport = relationship('PJSIPTransport')
    context = relationship('Context')
    parents = relationship(
        'EndpointSIP',
        primaryjoin='EndpointSIP.uuid==endpoint_sip_parent.c.child_uuid',
        secondaryjoin='EndpointSIP.uuid==endpoint_sip_parent.c.parent_uuid',
        secondary=parent_child,
    )

    _aor_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.aor_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.auth_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _endpoint_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.endpoint_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _registration_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.registration_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _registration_outbound_auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.registration_outbound_auth_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _identify_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.identify_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    _outbound_auth_section = relationship(
        'EndpointSIPSection',
        primaryjoin='EndpointSIPSection.uuid == EndpointSIP.outbound_auth_section_uuid',
        cascade='all, delete-orphan',
        single_parent=True,
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
        transport=None,
        context=None,
        caller_id=None,
        **kwargs
    ):
        if transport:
            kwargs['transport_uuid'] = transport['uuid']
        if context:
            kwargs['context_id'] = context['id']
        if aor_section_options:
            section = EndpointSIPSection(options=aor_section_options)
            kwargs['_aor_section'] = section
        if auth_section_options:
            section = EndpointSIPSection(options=auth_section_options)
            kwargs['_auth_section'] = section
        if endpoint_section_options:
            section = EndpointSIPSection(options=endpoint_section_options)
            kwargs['_endpoint_section'] = section
        if registration_section_options:
            section = EndpointSIPSection(options=registration_section_options)
            kwargs['_registration_section'] = section
        if registration_outbound_auth_section_options:
            section = EndpointSIPSection(options=registration_outbound_auth_section_options)
            kwargs['_registration_outbound_auth_section'] = section
        if identify_section_options:
            section = EndpointSIPSection(options=identify_section_options)
            kwargs['_identify_section'] = section
        if outbound_auth_section_options:
            section = EndpointSIPSection(options=outbound_auth_section_options)
            kwargs['_outbound_auth_section'] = section
        super(EndpointSIP, self).__init__(*args, **kwargs)
        if caller_id:
            self.caller_id = caller_id

    def __repr__(self):
        return 'EndpointSIP(display_name={}'.format(self.display_name)

    @hybrid_property
    def aor_section_options(self):
        return self._get_section_options(self._aor_section)

    @aor_section_options.setter
    def aor_section_options(self, options):
        if not self._aor_section:
            self._aor_section = EndpointSIPSection(options=options)
        elif options:
            self._aor_section.options = options
        else:
            self._aor_section = None

    @hybrid_property
    def auth_section_options(self):
        return self._get_section_options(self._auth_section)

    @auth_section_options.setter
    def auth_section_options(self, options):
        if not self._auth_section:
            self._auth_section = EndpointSIPSection(options=options)
        elif options:
            self._auth_section.options = options
        else:
            self._auth_section = None

    @hybrid_property
    def endpoint_section_options(self):
        return self._get_section_options(self._endpoint_section)

    @endpoint_section_options.setter
    def endpoint_section_options(self, options):
        if not self._endpoint_section:
            self._endpoint_section = EndpointSIPSection(options=options)
        elif options:
            self._endpoint_section.options = options
        else:
            self._endpoint_section = None

    @hybrid_property
    def registration_section_options(self):
        return self._get_section_options(self._registration_section)

    @registration_section_options.setter
    def registration_section_options(self, options):
        if not self._registration_section:
            self._registration_section = EndpointSIPSection(options=options)
        elif options:
            self._registration_section.options = options
        else:
            self._registration_section = None

    @hybrid_property
    def registration_outbound_auth_section_options(self):
        return self._get_section_options(self._registration_outbound_auth_section)

    @registration_outbound_auth_section_options.setter
    def registration_outbound_auth_section_options(self, options):
        if not self._registration_outbound_auth_section:
            self._registration_outbound_auth_section = EndpointSIPSection(options=options)
        elif options:
            self._registration_outbound_auth_section.options = options
        else:
            self._registration_outbound_auth_section = None

    @hybrid_property
    def identify_section_options(self):
        return self._get_section_options(self._identify_section)

    @identify_section_options.setter
    def identify_section_options(self, options):
        if not self._identify_section:
            self._identify_section = EndpointSIPSection(options=options)
        elif options:
            self._identify_section.options = options
        else:
            self._identify_section = None

    @hybrid_property
    def outbound_auth_section_options(self):
        return self._get_section_options(self._outbound_auth_section)

    @outbound_auth_section_options.setter
    def outbound_auth_section_options(self, options):
        if not self._outbound_auth_section:
            self._outbound_auth_section = EndpointSIPSection(options=options)
        elif options:
            self._outbound_auth_section.options = options
        else:
            self._outbound_auth_section = None

    def _get_section_options(self, section):
        if not section:
            return []

        return [[option.key, option.value] for option in section.options]

    line = relationship('LineFeatures', uselist=False)
    trunk = relationship('TrunkFeatures', uselist=False)

    @hybrid_property
    def caller_id(self):
        if not self._endpoint_section:
            return

        matching_options = self._endpoint_section.find('callerid')
        for key, value in matching_options:
            return value

    @caller_id.setter
    def caller_id(self, caller_id):
        if not self._endpoint_section:
            self._endpoint_section = EndpointSIPSection()

        self._endpoint_section.add_or_replace('callerid', caller_id)

    def update_caller_id(self, user, extension=None):
        # Copied from usersip
        name, num = user.extrapolate_caller_id(extension)
        caller_id = '"{}"'.format(name)
        if num:
            caller_id += " <{}>".format(num)
        self.caller_id = caller_id

    def endpoint_protocol(self):
        return 'sip'

    @hybrid_property
    def username(self):
        return self._find_first_value(self._auth_section, 'username')

    @username.expression
    def username(cls):
        return select(
            [EndpointSIPSectionOption.value]
        ).where(
            and_(
                cls.auth_section_uuid == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.endpoint_sip_section_uuid == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.key == 'username',
            )
        ).as_scalar()

    @hybrid_property
    def password(self):
        return self._find_first_value(self._auth_section, 'password')

    @password.expression
    def password(cls):
        return select(
            [EndpointSIPSectionOption.value]
        ).where(
            and_(
                cls.auth_section_uuid == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.endpoint_sip_section_uuid == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.key == 'password',
            )
        ).as_scalar()

    def _find_first_value(self, section, key):
        if not section:
            return
        matching_options = section.find(key)
        for _, value in matching_options:
            return value
