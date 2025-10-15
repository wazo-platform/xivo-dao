# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import Index, UniqueConstraint
from sqlalchemy.types import String, Text

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import Base

from .userfeatures import UserFeatures


class Blocklist(Base):
    __tablename__ = 'blocklist'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        Index('blocklist__idx__tenant_uuid', 'tenant_uuid'),
    )

    uuid = Column(UUID(as_uuid=False), server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(
        String(36),
        ForeignKey(Tenant.uuid, ondelete='CASCADE'),
        nullable=False,
    )

    tenant = relationship(Tenant, uselist=False)
    numbers = relationship(lambda: BlocklistNumber, back_populates='blocklist')
    user = relationship(
        UserFeatures,
        secondary=lambda: BlocklistUser.__table__,
        uselist=False,
        viewonly=True,
    )
    _user_link = relationship(lambda: BlocklistUser, lazy='joined', uselist=False)

    user_uuid = association_proxy(
        '_user_link',
        'user_uuid',
        creator=lambda user_uuid: BlocklistUser(user_uuid=user_uuid),
    )


class BlocklistNumber(Base):
    __tablename__ = 'blocklist_number'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        # NOTE: unique constraint also serves as index on number and blocklist_uuid
        UniqueConstraint(
            'number',
            'blocklist_uuid',
            name='blocklist_number_number_blocklist_uuid_key',
        ),
    )

    uuid = Column(UUID(as_uuid=False), server_default=text('uuid_generate_v4()'))
    number = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    blocklist_uuid = Column(
        UUID(as_uuid=False),
        ForeignKey(Blocklist.uuid, ondelete='CASCADE'),
        nullable=False,
    )

    tenant_uuid = association_proxy(
        'blocklist',
        'tenant_uuid',
    )

    blocklist = relationship(
        Blocklist,
        lazy='joined',
        uselist=False,
        back_populates='numbers',
    )

    @hybrid_property
    def user_uuid(self):
        return self.blocklist.user_uuid

    @user_uuid.expression
    def user_uuid(cls):
        query = (
            select(BlocklistUser.user_uuid)
            .where(BlocklistUser.blocklist_uuid == cls.blocklist_uuid)
            .label('user_uuid')
        )
        return query


class BlocklistUser(Base):
    __tablename__ = 'blocklist_user'
    __table_args__ = (PrimaryKeyConstraint('user_uuid', 'blocklist_uuid'),)

    user_uuid = Column(
        String(36),
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
