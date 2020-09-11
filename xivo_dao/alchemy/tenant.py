# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.types import String, Boolean
from xivo_dao.helpers.db_manager import Base


class Tenant(Base):

    __tablename__ = 'tenant'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(36), server_default=text('uuid_generate_v4()'))
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
    webrtc_video_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_webrtc_video_sip_template_uuid_fkey',
        ),
    )
    global_trunk_sip_template_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'endpoint_sip.uuid',
            ondelete='SET NULL',
            # NOTE(fblackburn): FK must be named to avoid circular deps on DROP
            name='tenant_global_trunk_sip_template_uuid_fkey',
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
