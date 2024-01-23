# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    ForeignKeyConstraint,
    CheckConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestCustom(Base):
    DESTINATION_TYPE_ID = 10

    __tablename__ = 'func_key_dest_custom'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id'),
        ForeignKeyConstraint(
            ('func_key_id', 'destination_type_id'),
            ('func_key.id', 'func_key.destination_type_id'),
        ),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default=f"{DESTINATION_TYPE_ID}")
    exten = Column(String(40), nullable=False)

    type = 'custom'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)

    def to_tuple(self):
        return (('exten', self.exten),)
