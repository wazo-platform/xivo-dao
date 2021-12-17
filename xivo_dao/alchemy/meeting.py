# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import (
    Boolean,
    DateTime,
    String,
    Text
)
from xivo_dao.helpers.db_manager import Base


class MeetingOwner(Base):

    __tablename__ = 'meeting_owner'

    meeting_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('meeting.uuid', ondelete='CASCADE'),
        primary_key=True,
    )
    user_uuid = Column(
        String(38),  # 38 is copied from userfeatures.uuid
        ForeignKey('userfeatures.uuid', ondelete='CASCADE'),
        primary_key=True,
    )

    owner = relationship('UserFeatures', foreign_keys='MeetingOwner.user_uuid')


class Meeting(Base):

    __tablename__ = 'meeting'
    __table_args__ = (
        UniqueConstraint('number', 'tenant_uuid'),
    )

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True)
    name = Column(Text)
    guest_endpoint_sip_uuid = Column(UUID(as_uuid=True), ForeignKey('endpoint_sip.uuid', ondelete='SET NULL'))
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, server_default=text("(now() at time zone 'utc')"))
    persistent = Column(Boolean, server_default='false', nullable=False)
    number = Column(Text, nullable=False)

    meeting_owners = relationship(
        'MeetingOwner',
        cascade='all, delete-orphan',
    )
    owners = association_proxy(
        'meeting_owners',
        'owner',
        creator=lambda owner: MeetingOwner(owner=owner)
    )
    guest_endpoint_sip = relationship(
        'EndpointSIP',
        cascade='all, delete-orphan',
        single_parent=True,
    )
    ingress_http = relationship(
        'IngressHTTP',
        foreign_keys='IngressHTTP.tenant_uuid',
        uselist=False,
        viewonly=True,
        primaryjoin='Meeting.tenant_uuid == IngressHTTP.tenant_uuid',
    )

    @property
    def owner_uuids(self):
        return [owner.uuid for owner in self.owners]
