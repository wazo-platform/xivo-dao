# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.types import Text

from xivo_dao.helpers.db_manager import Base


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
        ForeignKey('blocklist.uuid', ondelete='CASCADE'),
        nullable=False,
    )

    blocklist = relationship(
        'Blocklist',
        lazy='joined',
        uselist=False,
        back_populates='numbers',
    )
    tenant_uuid = association_proxy('blocklist', 'tenant_uuid')

    @hybrid_property
    def user_uuid(self):
        return self.blocklist.user_uuid

    @user_uuid.expression
    def user_uuid(cls):
        from .blocklist_user import BlocklistUser

        query = (
            select(BlocklistUser.user_uuid)
            .where(BlocklistUser.blocklist_uuid == cls.blocklist_uuid)
            .label('user_uuid')
        )
        return query
