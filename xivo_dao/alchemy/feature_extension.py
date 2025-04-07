# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Boolean, String
from xivo.xivo_helpers import clean_extension

from xivo_dao.helpers.db_manager import Base


class FeatureExtension(Base):
    __tablename__ = 'feature_extension'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('exten'),
    )

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    enabled = Column(Boolean, nullable=False, server_default='true')
    exten = Column(String(40), nullable=False)
    feature = Column(String(255), nullable=False)

    def is_pattern(self):
        return self.exten.startswith('_')

    def clean_exten(self):
        return clean_extension(self.exten)
