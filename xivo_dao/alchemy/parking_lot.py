# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class ParkingLot(Base):

    __tablename__ = 'parking_lot'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
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
        back_populates='parking_lot')

    def in_slots_range(self, exten):
        exten = int(exten)
        start = int(self.slots_start)
        end = int(self.slots_end)

        if start <= exten <= end:
            return True
        return False
