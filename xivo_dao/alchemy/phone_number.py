# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import (
    Column,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import text
from sqlalchemy.types import Boolean, String, Text

from xivo_dao.helpers.db_manager import Base


class PhoneNumber(Base):
    __tablename__ = 'phone_number'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        ForeignKeyConstraint(
            ('tenant_uuid',),
            ('tenant.uuid',),
            ondelete='CASCADE',
        ),
    )
    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(String(36), nullable=False)
    number = Column(Text, nullable=False)
    caller_id_name = Column(Text, nullable=True)
    shareable = Column(Boolean, nullable=False, server_default=text('false'))
    main = Column(Boolean, nullable=False, server_default=text('false'))

    def __repr__(self):
        return f'{self.__class__.__name__}(uuid={self.uuid}, number={self.number})'
