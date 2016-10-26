# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.db_manager import Base


class IVRChoice(Base):

    __tablename__ = 'ivr_choice'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    ivr_id = Column(Integer, ForeignKey('ivr.id'), nullable=False)
    exten = Column(String(40), nullable=False)

    dialaction = relationship(Dialaction,
                              primaryjoin="""and_(Dialaction.category == 'ivr_choice',
                                                  Dialaction.categoryval == cast(IVRChoice.id, String))""",
                              foreign_keys='Dialaction.categoryval',
                              uselist=False,
                              cascade='all, delete-orphan')

    @property
    def destination(self):
        return self.dialaction

    @destination.setter
    def destination(self, destination):
        if not self.dialaction:
            destination.event = 'ivr_choice'
            destination.category = 'ivr_choice'
            destination.linked = 1
            self.dialaction = destination

        self.dialaction.action = destination.action
        self.dialaction.actionarg1 = destination.actionarg1
        self.dialaction.actionarg2 = destination.actionarg2
