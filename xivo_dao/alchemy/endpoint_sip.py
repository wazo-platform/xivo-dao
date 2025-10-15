# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from sqlalchemy import column, select, table, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip_section import (
    AORSection,
    AuthSection,
    EndpointSection,
    IdentifySection,
    OutboundAuthSection,
    RegistrationOutboundAuthSection,
    RegistrationSection,
)

logger = logging.getLogger(__name__)


class EndpointSIPTemplate(Base):
    __tablename__ = 'endpoint_sip_template'

    child_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='CASCADE'),
        primary_key=True,
    )
    parent_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='CASCADE'),
        primary_key=True,
    )
    priority = Column(Integer)

    parent = relationship('EndpointSIP', foreign_keys='EndpointSIPTemplate.parent_uuid')


class EndpointSIP(Base):
    __tablename__ = 'endpoint_sip'
    __table_args__ = (UniqueConstraint('name'),)

    uuid = Column(
        UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True
    )
    label = Column(Text)
    name = Column(Text, nullable=False)
    asterisk_id = Column(Text)
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    transport_uuid = Column(UUID(as_uuid=True), ForeignKey('pjsip_transport.uuid'))
    template = Column(Boolean, server_default=text('false'))

    transport = relationship('PJSIPTransport')
    template_relations = relationship(
        'EndpointSIPTemplate',
        primaryjoin='EndpointSIP.uuid == EndpointSIPTemplate.child_uuid',
        cascade='all, delete-orphan',
        order_by='EndpointSIPTemplate.priority',
        collection_class=ordering_list('priority'),
    )
    templates = association_proxy(
        'template_relations',
        'parent',
        creator=lambda _sip: EndpointSIPTemplate(parent=_sip),
    )
    _options = column_property(
        select(column('options'))
        .where(column('root') == uuid)
        .select_from(table('endpoint_sip_options_view'))
        .scalar_subquery(),
        deferred=True,
    )
    _aor_section = relationship(
        'AORSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _auth_section = relationship(
        'AuthSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _endpoint_section = relationship(
        'EndpointSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _registration_section = relationship(
        'RegistrationSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _registration_outbound_auth_section = relationship(
        'RegistrationOutboundAuthSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _identify_section = relationship(
        'IdentifySection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    _outbound_auth_section = relationship(
        'OutboundAuthSection',
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __init__(
        self,
        aor_section_options=None,
        auth_section_options=None,
        endpoint_section_options=None,
        registration_section_options=None,
        registration_outbound_auth_section_options=None,
        identify_section_options=None,
        outbound_auth_section_options=None,
        caller_id=None,
        *args,
        **kwargs,
    ):
        if aor_section_options:
            kwargs['_aor_section'] = AORSection(
                options=aor_section_options,
            )
        if auth_section_options:
            kwargs['_auth_section'] = AuthSection(
                options=auth_section_options,
            )
        if endpoint_section_options:
            kwargs['_endpoint_section'] = EndpointSection(
                options=endpoint_section_options,
            )
        if registration_section_options:
            kwargs['_registration_section'] = RegistrationSection(
                options=registration_section_options,
            )
        if registration_outbound_auth_section_options:
            kwargs[
                '_registration_outbound_auth_section'
            ] = RegistrationOutboundAuthSection(
                options=registration_outbound_auth_section_options,
            )
        if identify_section_options:
            kwargs['_identify_section'] = IdentifySection(
                options=identify_section_options,
            )
        if outbound_auth_section_options:
            kwargs['_outbound_auth_section'] = OutboundAuthSection(
                options=outbound_auth_section_options,
            )
        super().__init__(*args, **kwargs)
        if caller_id:
            self.caller_id = caller_id

    def __repr__(self):
        return f'EndpointSIP(label={self.label})'

    @hybrid_property
    def aor_section_options(self):
        if not self._aor_section:
            return []
        return self._aor_section.options

    @aor_section_options.setter
    def aor_section_options(self, options):
        if not self._aor_section:
            self._aor_section = AORSection(options=options)
        elif options:
            self._aor_section.options = options
        else:
            self._aor_section = None

    @hybrid_property
    def auth_section_options(self):
        if not self._auth_section:
            return []
        return self._auth_section.options

    @auth_section_options.setter
    def auth_section_options(self, options):
        if not self._auth_section:
            self._auth_section = AuthSection(options=options)
        elif options:
            self._auth_section.options = options
        else:
            self._auth_section = None

    @hybrid_property
    def endpoint_section_options(self):
        if not self._endpoint_section:
            return []
        return self._endpoint_section.options

    @endpoint_section_options.setter
    def endpoint_section_options(self, options):
        if not self._endpoint_section:
            self._endpoint_section = EndpointSection(options=options)
        elif options:
            self._endpoint_section.options = options
        else:
            self._endpoint_section = None

    def _get_combined_section_options(self, section_name):
        inherited_options = getattr(self, f'inherited_{section_name}_section_options')
        endpoint_options = getattr(self, f'{section_name}_section_options')
        return inherited_options + endpoint_options

    @hybrid_property
    def combined_aor_section_options(self):
        return self._get_combined_section_options('aor')

    @hybrid_property
    def combined_auth_section_options(self):
        return self._get_combined_section_options('auth')

    @hybrid_property
    def combined_endpoint_section_options(self):
        return self._get_combined_section_options('endpoint')

    @hybrid_property
    def combined_registration_section_options(self):
        return self._get_combined_section_options('registration')

    @hybrid_property
    def combined_registration_outbound_auth_section_options(self):
        return self._get_combined_section_options('registration_outbound_auth')

    @hybrid_property
    def combined_identify_section_options(self):
        return self._get_combined_section_options('identify')

    @hybrid_property
    def combined_outbound_auth_section_options(self):
        return self._get_combined_section_options('outbound_auth')

    def _get_inherited_section_options(self, section_name):
        if not self.templates:
            return []

        options = []
        for template in self.templates:
            template_options = getattr(
                template,
                f'combined_{section_name}_section_options',
            )
            for k, v in template_options:
                options.append([k, v])
        return options

    @hybrid_property
    def inherited_aor_section_options(self):
        return self._get_inherited_section_options('aor')

    @hybrid_property
    def inherited_auth_section_options(self):
        return self._get_inherited_section_options('auth')

    @hybrid_property
    def inherited_endpoint_section_options(self):
        return self._get_inherited_section_options('endpoint')

    @hybrid_property
    def inherited_registration_section_options(self):
        return self._get_inherited_section_options('registration')

    @hybrid_property
    def inherited_registration_outbound_auth_section_options(self):
        return self._get_inherited_section_options('registration_outbound_auth')

    @hybrid_property
    def inherited_identify_section_options(self):
        return self._get_inherited_section_options('identify')

    @hybrid_property
    def inherited_outbound_auth_section_options(self):
        return self._get_inherited_section_options('outbound_auth')

    @hybrid_property
    def registration_section_options(self):
        if not self._registration_section:
            return []
        return self._registration_section.options

    @registration_section_options.setter
    def registration_section_options(self, options):
        if not self._registration_section:
            self._registration_section = RegistrationSection(options=options)
        elif options:
            self._registration_section.options = options
        else:
            self._registration_section = None

    @hybrid_property
    def registration_outbound_auth_section_options(self):
        if not self._registration_outbound_auth_section:
            return []
        return self._registration_outbound_auth_section.options

    @registration_outbound_auth_section_options.setter
    def registration_outbound_auth_section_options(self, options):
        if not self._registration_outbound_auth_section:
            self._registration_outbound_auth_section = RegistrationOutboundAuthSection(
                options=options,
            )
        elif options:
            self._registration_outbound_auth_section.options = options
        else:
            self._registration_outbound_auth_section = None

    @hybrid_property
    def identify_section_options(self):
        if not self._identify_section:
            return []
        return self._identify_section.options

    @identify_section_options.setter
    def identify_section_options(self, options):
        if not self._identify_section:
            self._identify_section = IdentifySection(options=options)
        elif options:
            self._identify_section.options = options
        else:
            self._identify_section = None

    @hybrid_property
    def outbound_auth_section_options(self):
        if not self._outbound_auth_section:
            return []
        return self._outbound_auth_section.options

    @outbound_auth_section_options.setter
    def outbound_auth_section_options(self, options):
        if not self._outbound_auth_section:
            self._outbound_auth_section = OutboundAuthSection(options=options)
        elif options:
            self._outbound_auth_section.options = options
        else:
            self._outbound_auth_section = None

    line = relationship('LineFeatures', uselist=False)
    trunk = relationship('TrunkFeatures', uselist=False)

    @hybrid_property
    def caller_id(self):
        if not self._endpoint_section:
            return

        matching_options = self._endpoint_section.find('callerid')
        for key, value in matching_options:
            return value

    @caller_id.expression
    def caller_id(cls):
        return cls._query_option_value('callerid')

    @caller_id.setter
    def caller_id(self, caller_id):
        if not self._endpoint_section:
            self._endpoint_section = EndpointSection()

        self._endpoint_section.add_or_replace('callerid', caller_id)

    def update_caller_id(self, user, extension=None):
        # Copied from old table
        name, num = user.extrapolate_caller_id(extension)
        caller_id = f'"{name}"'
        if num:
            caller_id += f" <{num}>"
        self.caller_id = caller_id

    def endpoint_protocol(self):
        return 'sip'

    @property
    def username(self):
        return self._find_first_value(self._auth_section, 'username')

    @property
    def password(self):
        return self._find_first_value(self._auth_section, 'password')

    def _find_first_value(self, section, key):
        if not section:
            return
        matching_options = section.find(key)
        for _, value in matching_options:
            return value

    def get_option_value(self, option):
        if not self._options:
            return None
        return self._options.get(option, None)

    @classmethod
    def _query_option_value(cls, option):
        if option is None:
            return None

        return cls._options.remote_attr[option].astext
