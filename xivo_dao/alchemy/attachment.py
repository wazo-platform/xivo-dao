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

from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Binary

from xivo_dao.helpers.db_manager import Base


class Attachment(Base):

    __tablename__ = 'attachment'
    __table_args__ = (
        UniqueConstraint('object_type', 'object_id'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    object_type = Column(String(16), nullable=False)
    object_id = Column(Integer, nullable=False)
    file = Column(Binary)
    size = Column(Integer, nullable=False)
    mime = Column(String(64), nullable=False)
