# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import cast

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestParkPosition(Base):
    DESTINATION_TYPE_ID = 7

    __tablename__ = 'func_key_dest_park_position'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id'),
        ForeignKeyConstraint(
            ('func_key_id', 'destination_type_id'),
            ('func_key.id', 'func_key.destination_type_id'),
        ),
        UniqueConstraint('parking_lot_uuid', 'park_position'),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
        CheckConstraint("park_position ~ '^[0-9]+$'"),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default=f"{DESTINATION_TYPE_ID}")
    parking_lot_uuid = Column(UUID(as_uuid=True), ForeignKey('parking_lot.uuid'), nullable=False)
    park_position = Column(String(40), nullable=False)

    type = 'park_position'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)
    parking_lot = relationship(ParkingLot)

    def to_tuple(self):
        return (
            ('parking_lot_uuid', self.parking_lot_uuid),
            ('position', self.position),
        )

    @hybrid_property
    def position(self):
        return int(self.park_position)

    @position.expression
    def position(cls):
        return cast(cls.park_position, Integer)

    @position.setter
    def position(self, value):
        self.park_position = value
