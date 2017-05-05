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

from sqlalchemy import Enum
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Index
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class CallLogParticipant(Base):

    __tablename__ = 'call_log_participant'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        Index('call_log_participant__idx__user_uuid', 'user_uuid'),
    )

    uuid = Column(String(38), default=new_uuid)
    call_log_id = Column(Integer, ForeignKey('call_log.id', name='fk_call_log_id', ondelete='CASCADE'))
    user_uuid = Column(String(38), nullable=False)
    line_id = Column(Integer)
    role = Column('role', Enum('source', 'destination', name='call_log_participant_role'), nullable=False)
