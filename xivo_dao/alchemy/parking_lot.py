# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class ParkingLot(Base):

    __tablename__ = 'parking_lot'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    name = Column(String(128))
    slots_start = Column(String(40), nullable=False)
    slots_end = Column(String(40), nullable=False)
    timeout = Column(Integer)
    music_on_hold = Column(String(128))

    extensions = relationship('Extension',
                              primaryjoin="""and_(Extension.type == 'parking',
                                                  Extension.typeval == cast(ParkingLot.id, String))""",
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
