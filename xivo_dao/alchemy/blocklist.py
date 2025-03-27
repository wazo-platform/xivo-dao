# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import (
    Column,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import Index, UniqueConstraint
from sqlalchemy.types import Text, String
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import Base
from .userfeatures import UserFeatures


class Blocklist(Base):
    __tablename__ = 'blocklist'
    __table_args__ = (PrimaryKeyConstraint('uuid'),)

    uuid = Column(UUID(as_uuid=False), server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(
        String(38),
        ForeignKey(Tenant.uuid, ondelete='CASCADE'),
        nullable=False,
    )

    tenant = relationship(Tenant, lazy='joined', uselist=False)
    numbers = relationship(lambda: BlocklistNumber, lazy='joined')
    user = relationship(
        UserFeatures,
        secondary=lambda: BlocklistUser.__table__,
        lazy='joined',
        backref='blocklist',
        uselist=False,
    )
    _user_link = relationship(lambda: BlocklistUser, uselist=False)

    user_uuid = association_proxy(
        '_user_link',
        'user_uuid',
        creator=lambda user_uuid: BlocklistUser(user_uuid=user_uuid),
    )


class BlocklistNumber(Base):
    __tablename__ = 'blocklist_number'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('number', 'blocklist_uuid'),
    )

    uuid = Column(UUID(as_uuid=False), server_default=text('uuid_generate_v4()'))
    number = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    blocklist_uuid = Column(
        UUID(as_uuid=False),
        ForeignKey(Blocklist.uuid, ondelete='CASCADE'),
        nullable=False,
    )

    blocklist = relationship(Blocklist, lazy='joined', uselist=False)

    user_uuid = association_proxy('blocklist', 'user_uuid')


class BlocklistUser(Base):
    __tablename__ = 'blocklist_user'
    __table_args__ = (PrimaryKeyConstraint('user_uuid', 'blocklist_uuid'),)

    user_uuid = Column(
        String(38),
        ForeignKey(
            UserFeatures.uuid, ondelete='CASCADE', name='blocklist_user_user_uuid_fkey'
        ),
        nullable=False,
    )
    blocklist_uuid = Column(
        UUID(as_uuid=False),
        ForeignKey(
            Blocklist.uuid,
            ondelete='CASCADE',
            name='blocklist_user_blocklist_uuid_fkey',
        ),
        nullable=False,
    )
