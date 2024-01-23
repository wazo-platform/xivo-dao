# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import String, Boolean
from xivo_dao.helpers.db_manager import Base


class Tenant(Base):
    __tablename__ = 'tenant'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        Index('tenant__idx__global_sip_template_uuid', 'global_sip_template_uuid'),
        Index('tenant__idx__webrtc_sip_template_uuid', 'webrtc_sip_template_uuid'),
        Index(
            'tenant__idx__registration_trunk_sip_template_uuid',
            'registration_trunk_sip_template_uuid',
        ),
        Index(
            'tenant__idx__meeting_guest_sip_template_uuid',
            'meeting_guest_sip_template_uuid',
        ),
        Index(
            'tenant__idx__twilio_trunk_sip_template_uuid',
            'twilio_trunk_sip_template_uuid',
        ),
    )

    uuid = Column(String(36), server_default=text('uuid_generate_v4()'))
    slug = Column(String(10))
    sip_templates_generated = Column(Boolean, nullable=False, server_default='false')
    global_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_global_sip_template_uuid_fkey',
        ),
    )
    webrtc_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_webrtc_sip_template_uuid_fkey',
        ),
    )
    registration_trunk_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_registration_trunk_sip_template_uuid_fkey',
        ),
    )
    meeting_guest_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_meeting_guest_sip_template_uuid_fkey',
        ),
    )
    twilio_trunk_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_twilio_trunk_sip_template_uuid_fkey',
        ),
    )

    global_sip_template = relationship(
        'EndpointSIP',
        uselist=False,
        primaryjoin='EndpointSIP.uuid == Tenant.global_sip_template_uuid',
        viewonly=True,
    )
    webrtc_sip_template = relationship(
        'EndpointSIP',
        uselist=False,
        primaryjoin='EndpointSIP.uuid == Tenant.webrtc_sip_template_uuid',
        viewonly=True,
    )
    registration_trunk_sip_template = relationship(
        'EndpointSIP',
        uselist=False,
        primaryjoin='EndpointSIP.uuid == Tenant.registration_trunk_sip_template_uuid',
        viewonly=True,
    )
    meeting_guest_sip_template = relationship(
        'EndpointSIP',
        uselist=False,
        primaryjoin='EndpointSIP.uuid == Tenant.meeting_guest_sip_template_uuid',
        viewonly=True,
    )
