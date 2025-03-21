# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import (
    Column,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import text
from sqlalchemy.types import Text, String
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base
from .userfeatures import UserFeatures


class BlocklistNumber(Base):
    __tablename__ = 'blocklist_number'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('number', 'user_uuid'),
        UniqueConstraint('label', 'user_uuid'),
    )

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    number = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    user_uuid = Column(
        String(38),
        ForeignKey(UserFeatures.uuid, ondelete='CASCADE'),
        nullable=False,
    )

    user = relationship("UserFeatures", foreign_keys=[user_uuid], lazy='joined')

    def __repr__(self):
        return f'{self.__class__.__name__}(uuid={self.uuid}, number={self.number})'
