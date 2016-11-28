# -*- coding: utf-8 -*-

# Copyright (C) 2016 Francois Blackburn
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Boolean

from xivo_dao.helpers.db_manager import Base


class Conference(Base):

    __tablename__ = 'conference'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    name = Column(String(128))
    preprocess_subroutine = Column(String(39))

    max_users = Column(Integer, nullable=False, server_default='50')
    record = Column(Boolean, nullable=False, server_default='False')

    pin = Column(String(80))
    notify_join_leave = Column(Boolean, nullable=False, server_default='True')
    announce_join_leave = Column(Boolean, nullable=False, server_default='False')
    announce_user_count = Column(Boolean, nullable=False, server_default='False')
    announce_only_user = Column(Boolean, nullable=False, server_default='True')
    music_on_hold = Column(String(128))

    admin_pin = Column(String(80))
