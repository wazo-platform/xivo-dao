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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class ContextMember(Base):

    __tablename__ = 'contextmember'
    __table_args__ = (
        PrimaryKeyConstraint('context', 'type', 'typeval', 'varname'),
        Index('contextmember__idx__context', 'context'),
        Index('contextmember__idx__context_type', 'context', 'type'),
    )

    context = Column(String(39))
    type = Column(String(32))
    typeval = Column(String(128), server_default='')
    varname = Column(String(128), server_default='')
