# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import (
    Column,
    ForeignKey,
)
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.db_manager import UUIDAsString


class Application(Base):
    __tablename__ = 'application'
    __table_args__ = (Index('application__idx__tenant_uuid', 'tenant_uuid'),)

    uuid = Column(
        UUIDAsString(36), primary_key=True, server_default=text('uuid_generate_v4()')
    )
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    name = Column(String(128))

    dest_node = relationship(
        'ApplicationDestNode',
        cascade='all, delete-orphan',
        passive_deletes=True,
        uselist=False,
    )

    lines = relationship('LineFeatures', viewonly=True)

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.action == 'application:custom',
            Dialaction.actionarg1 == Application.uuid
        )""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
    )
