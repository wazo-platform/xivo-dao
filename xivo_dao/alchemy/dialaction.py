# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class Dialaction(Base):

    USER_EVENTS = ('noanswer',
                   'busy',
                   'congestion',
                   'chanunavail')

    __tablename__ = 'dialaction'
    __table_args__ = (
        PrimaryKeyConstraint('event', 'category', 'categoryval'),
        Index('dialaction__idx__action_actionarg1', 'action', 'actionarg1'),
    )

    event = Column(enum.dialaction_event)
    category = Column(enum.dialaction_category)
    categoryval = Column(String(128), server_default='')
    action = Column(enum.dialaction_action, nullable=False)
    actionarg1 = Column(String(255))
    actionarg2 = Column(String(255))
    linked = Column(Integer, nullable=False, server_default='0')

    @classmethod
    def new_user_actions(cls, user):
        for event in cls.USER_EVENTS:
            yield cls(event=event,
                      category='user',
                      categoryval=str(user.id),
                      action='none',
                      actionarg1=None,
                      actionarg2=None,
                      linked=1)
