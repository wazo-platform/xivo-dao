# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.sql import cast, select
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base

from .extension import Extension


class ParkingLot(Base):
    __tablename__ = 'parking_lot'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('parking_lot__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128))
    slots_start = Column(String(40), nullable=False)
    slots_end = Column(String(40), nullable=False)
    timeout = Column(Integer)
    music_on_hold = Column(String(128))

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(
            Extension.type == 'parking',
            Extension.typeval == cast(ParkingLot.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    func_keys_park_position = relationship(
        'FuncKeyDestParkPosition',
        cascade='all, delete-orphan',
    )

    func_keys_parking = relationship(
        'FuncKeyDestParking',
        cascade='all, delete-orphan',
    )

    def in_slots_range(self, exten):
        if not str(exten).isdigit() or str(exten).startswith('0'):
            return False

        exten = int(exten)
        start = int(self.slots_start)
        end = int(self.slots_end)

        if start <= exten <= end:
            return True
        return False

    @hybrid_property
    def exten(self):
        for extension in self.extensions:
            return extension.exten
        return None

    @exten.expression
    def exten(cls):
        return (
            select(Extension.exten)
            .where(Extension.type == 'parking')
            .where(Extension.typeval == cast(cls.id, String))
            .scalar_subquery()
        )

    @hybrid_property
    def context(self):
        for extension in self.extensions:
            return extension.context
        return None

    @context.expression
    def context(cls):
        return (
            select(Extension.context)
            .where(Extension.type == 'parking')
            .where(Extension.typeval == cast(cls.id, String))
            .scalar_subquery()
        )
