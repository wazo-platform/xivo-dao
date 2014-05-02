# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    CheckConstraint
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class ServerFeatures(Base):

    __tablename__ = 'serverfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        CheckConstraint('feature=\'phonebook\''),
        UniqueConstraint('serverid', 'feature', 'type'),
    )

    id = Column(Integer)
    serverid = Column(Integer, nullable=False)
    feature = Column(String(64), nullable=False)
    type = Column(Enum('xivo', 'ldap',
                       name='serverfeatures_type',
                       metadata=Base.metadata))
    commented = Column(Integer, nullable=False, server_default='0')
