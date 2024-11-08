# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import (
    Column,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.sql import text
from sqlalchemy.types import Boolean, String, Text
from sqlalchemy.ext.hybrid import hybrid_property

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
        UniqueConstraint('number', 'tenant_uuid'),
        Index(
            'only_one_main_allowed',
            'main',
            'tenant_uuid',
            unique=True,
            postgresql_where=(text('main is true')),
        ),
        CheckConstraint(
            'CASE WHEN main THEN shared ELSE true END',
            name='shared_if_main',
        ),
    )

    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(String(36), nullable=False)
    number = Column(Text, nullable=False)
    caller_id_name = Column(Text, nullable=True)
    shared = Column(Boolean, nullable=False, server_default=text('false'))
    _main = Column('main', Boolean, nullable=False, server_default=text('false'))

    @hybrid_property
    def main(self):
        return self._main

    @main.setter
    def main(self, value):
        self._main = value
        if value:
            self.shared = True

    def __repr__(self):
        return f'{self.__class__.__name__}(uuid={self.uuid}, number={self.number})'
