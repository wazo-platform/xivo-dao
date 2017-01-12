# -*- coding: utf-8 -*-
#
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

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class SwitchboardMemberUser(Base):

    __tablename__ = 'switchboard_member_user'
    __table_args__ = (
        PrimaryKeyConstraint('switchboard_id', 'user_uuid'),
        Index('switchboard_member_user__idx__switchboard_id', 'switchboard_id'),
    )

    switchboard_id = Column(Integer, ForeignKey('switchboard.id'), nullable=False)
    user_uuid = Column(String(38), ForeignKey('userfeatures.uuid'), nullable=False)

    switchboard = relationship('Switchboard')
    user = relationship('UserFeatures')
