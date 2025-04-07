# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.sql.schema import ForeignKey, Index
from sqlalchemy.types import DateTime, Text

from xivo_dao.helpers.datetime import utcnow_with_tzinfo
from xivo_dao.helpers.db_manager import Base


class MeetingAuthorization(Base):
    __tablename__ = 'meeting_authorization'
    __table_args__ = (
        Index('meeting_authorization__idx__guest_uuid', 'guest_uuid'),
        Index('meeting_authorization__idx__meeting_uuid', 'meeting_uuid'),
    )

    uuid = Column(
        UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True
    )
    guest_uuid = Column(UUID(as_uuid=True), nullable=False)
    meeting_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('meeting.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    guest_name = Column(Text)
    status = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=utcnow_with_tzinfo,
        server_default=text("(now() at time zone 'utc')"),
    )

    meeting = relationship(
        'Meeting',
        primaryjoin='Meeting.uuid == MeetingAuthorization.meeting_uuid',
        foreign_keys='MeetingAuthorization.meeting_uuid',
        viewonly=True,
    )
    guest_endpoint_sip = relationship(
        'EndpointSIP',
        secondary='meeting',
        secondaryjoin='EndpointSIP.uuid == Meeting.guest_endpoint_sip_uuid',
        primaryjoin='MeetingAuthorization.meeting_uuid == Meeting.uuid',
        viewonly=True,
        uselist=False,
    )
