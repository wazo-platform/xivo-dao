# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func

from xivo_dao.helpers.db_manager import Base, IntAsString
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

    event = Column(String(40))
    category = Column(enum.dialaction_category)
    categoryval = Column(IntAsString(128), server_default='')
    action = Column(enum.dialaction_action, nullable=False)
    actionarg1 = Column(IntAsString(255))
    actionarg2 = Column(String(255))
    linked = Column(Integer, nullable=False, server_default='0')

    group = relationship('GroupFeatures',
                         primaryjoin="""and_(Dialaction.action == 'group',
                                             Dialaction.actionarg1 == cast(GroupFeatures.id, String))""",
                         foreign_keys='Dialaction.actionarg1')

    user = relationship('UserFeatures',
                        primaryjoin="""and_(Dialaction.action == 'user',
                                            Dialaction.actionarg1 == cast(UserFeatures.id, String))""",
                        foreign_keys='Dialaction.actionarg1')

    ivr = relationship('IVR',
                       primaryjoin="""and_(Dialaction.action == 'ivr',
                                           Dialaction.actionarg1 == cast(IVR.id, String))""",
                       foreign_keys='Dialaction.actionarg1')

    voicemail = relationship('Voicemail',
                             primaryjoin="""and_(Dialaction.action == 'voicemail',
                                                 Dialaction.actionarg1 == cast(Voicemail.id, String))""",
                             foreign_keys='Dialaction.actionarg1')

    incall = relationship('Incall',
                          primaryjoin="""and_(Dialaction.category == 'incall',
                                              Dialaction.categoryval == cast(Incall.id, String))""",
                          foreign_keys='Dialaction.categoryval',
                          back_populates='dialaction')

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

    @hybrid_property
    def type(self):
        if not self.action:
            return
        return self.action.split(':', 1)[0]

    @type.expression
    def type(cls):
        return func.split_part(cls.action, ':', 1)

    @type.setter
    def type(self, type_):
        if not self.action:
            self.action = type_
            return
        type_subtype = self.action.split(':', 1)
        if len(type_subtype) == 2:
            self.action = '{}:{}'.format(type_, type_subtype[1])
        else:
            self.action = type_

    @hybrid_property
    def subtype(self):
        if not self.action:
            return
        type_subtype = self.action.split(':', 1)
        if len(type_subtype) == 2:
            return type_subtype[1]
        return None

    @subtype.expression
    def subtype(cls):
        return func.split_part(cls.action, ':', 2)

    @subtype.setter
    def subtype(self, subtype):
        self.action = '{}:{}'.format(self.type, subtype)

    @property
    def gosub_args(self):
        if not self.linked:
            return 'none'
        return ','.join(item or '' for item in (self.action, self.actionarg1, self.actionarg2))
