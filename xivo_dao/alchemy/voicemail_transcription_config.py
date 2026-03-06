# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Boolean, Column, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import ForeignKey, Index
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class VoicemailTranscriptionConfig(Base):
    __tablename__ = 'voicemail_transcription_config'
    __table_args__ = (
        Index('voicemail_transcription_config__idx__tenant_uuid', 'tenant_uuid'),
    )

    uuid = Column(
        UUID(as_uuid=True),
        server_default=text('uuid_generate_v4()'),
        primary_key=True,
    )
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        unique=True,
        nullable=False,
    )
    enabled = Column(Boolean, nullable=False, server_default=text('false'))
