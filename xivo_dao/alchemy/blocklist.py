# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import Index
from sqlalchemy.types import String

from xivo_dao.alchemy.blocklist_user import BlocklistUser
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import Base

from .userfeatures import UserFeatures


def _create_blocklist_user(user_uuid):
    return BlocklistUser(user_uuid=user_uuid)


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
    numbers = relationship('BlocklistNumber', back_populates='blocklist')
    user = relationship(
        UserFeatures,
        secondary='blocklist_user',
        uselist=False,
        viewonly=True,
    )
    _user_link = relationship('BlocklistUser', lazy='joined', uselist=False)

    user_uuid = association_proxy(
        '_user_link',
        'user_uuid',
        creator=_create_blocklist_user,
    )
