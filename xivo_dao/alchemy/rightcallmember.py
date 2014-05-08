# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class RightCallMember(Base):

    __tablename__ = 'rightcallmember'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('rightcallid', 'type', 'typeval'),
    )

    id = Column(Integer, nullable=False)
    rightcallid = Column(Integer, nullable=False, server_default='0')
    type = Column(Enum('user', 'group', 'incall', 'outcall',
                       name='rightcallmember_type',
                       metadata=Base.metadata),
                  nullable=False)
    typeval = Column(String(128), nullable=False, server_default='0')
