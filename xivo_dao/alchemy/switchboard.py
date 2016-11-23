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

import uuid

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


def _new_uuid():
    return str(uuid.uuid4())


class Switchboard(Base):

    __tablename__ = 'switchboard'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(String(38), nullable=False, default=_new_uuid)
    name = Column(String(128), nullable=False)

    incall_dialactions = relationship('Dialaction',
                                      primaryjoin="""and_(Dialaction.category == 'incall',
                                           Dialaction.action == 'switchboard',
                                           Dialaction.actionarg1 == Switchboard.id)""",
                                      foreign_keys='Dialaction.actionarg1',
                                      viewonly=True)

    incalls = association_proxy('incall_dialactions', 'incall')
