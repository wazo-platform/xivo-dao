# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class MOH(Base):
    __tablename__ = 'moh'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('name'),
        Index('moh__idx__tenant_uuid', 'tenant_uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    label = Column(Text, nullable=False)
    mode = Column(Text, nullable=False)
    application = Column(Text)
    sort = Column(Text)
