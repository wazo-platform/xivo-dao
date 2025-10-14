# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base

from .userfeatures import UserFeatures


class BlocklistUser(Base):
    __tablename__ = 'blocklist_user'
    __table_args__ = (PrimaryKeyConstraint('user_uuid', 'blocklist_uuid'),)

    user_uuid = Column(
        String(36),
        ForeignKey(
            UserFeatures.uuid,
            ondelete='CASCADE',
            name='blocklist_user_user_uuid_fkey',
        ),
        nullable=False,
    )
    blocklist_uuid = Column(
        UUID(as_uuid=False),
        ForeignKey(
            'blocklist.uuid',
            ondelete='CASCADE',
            name='blocklist_user_blocklist_uuid_fkey',
        ),
        nullable=False,
    )
