# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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
from sqlalchemy.types import String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class MOH(Base):

    __tablename__ = 'moh'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('name'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    name = Column(Text, nullable=False)
    label = Column(Text)
    mode = Column(Text, nullable=False)
    application = Column(Text)
    sort = Column(Text)
