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

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.types import Integer, Boolean
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint


class UserLine(Base):

    __tablename__ = 'user_line'
    __table_args__ = (
        UniqueConstraint('user_id', 'line_id'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('userfeatures.id'))
    line_id = Column(Integer, ForeignKey('linefeatures.id'), nullable=False, primary_key=True)
    extension_id = Column(Integer, ForeignKey('extensions.id'))
    main_user = Column(Boolean, nullable=False)
    main_line = Column(Boolean, nullable=False)
