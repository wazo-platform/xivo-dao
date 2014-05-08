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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class PagingUser(Base):

    __tablename__ = 'paginguser'
    __table_args__ = (
        PrimaryKeyConstraint('pagingid', 'userfeaturesid', 'caller'),
        Index('paginguser__idx__pagingid', 'pagingid'),
    )

    pagingid = Column(Integer, nullable=False, autoincrement=False)
    userfeaturesid = Column(Integer, nullable=False, autoincrement=False)
    caller = Column(Integer, nullable=False, autoincrement=False)
