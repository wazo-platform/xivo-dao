# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
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

    # Remove the following warning:
    #   SAWarning: DELETE statement on table 'dialaction' expected to delete 2 row(s); 1 were matched.
    #   Please set confirm_deleted_rows=False within the mapper configuration to prevent this warning.
    # When child try to delete parent and the parent try delete child,
    # then the same row expecte to be removed twice.
    # This is the case of ivr_choice
    __mapper_args__ = {'confirm_deleted_rows': False}

    event = Column(String(40))
    category = Column(enum.dialaction_category)
    categoryval = Column(IntAsString(128), server_default='')
    action = Column(enum.dialaction_action, nullable=False)
    actionarg1 = Column(IntAsString(255))
    actionarg2 = Column(String(255))
    linked = Column(Integer, nullable=False, server_default='0')

    conference = relationship('Conference',
                              primaryjoin="""and_(Dialaction.action == 'conference',
                                                  Dialaction.actionarg1 == cast(Conference.id, String))""",
                              foreign_keys='Dialaction.actionarg1',
                              viewonly=True)

    group = relationship('GroupFeatures',
                         primaryjoin="""and_(Dialaction.action == 'group',
                                             Dialaction.actionarg1 == cast(GroupFeatures.id, String))""",
                         foreign_keys='Dialaction.actionarg1',
                         viewonly=True)

    user = relationship('UserFeatures',
                        primaryjoin="""and_(Dialaction.action == 'user',
                                            Dialaction.actionarg1 == cast(UserFeatures.id, String))""",
                        foreign_keys='Dialaction.actionarg1',
                        viewonly=True)

    ivr = relationship('IVR',
                       primaryjoin="""and_(Dialaction.action == 'ivr',
                                           Dialaction.actionarg1 == cast(IVR.id, String))""",
                       foreign_keys='Dialaction.actionarg1',
                       viewonly=True)

    ivr_choice = relationship('IVRChoice',
                              primaryjoin="""and_(Dialaction.category == 'ivr_choice',
                                                  Dialaction.categoryval == cast(IVRChoice.id, String))""",
                              foreign_keys='Dialaction.categoryval',
                              cascade='delete',
                              back_populates='dialaction')

    switchboard = relationship('Switchboard',
                               primaryjoin="""and_(Dialaction.action == 'switchboard',
                                             Dialaction.actionarg1 == Switchboard.uuid)""",
                               foreign_keys='Dialaction.actionarg1',
                               viewonly=True)

    voicemail = relationship('Voicemail',
                             primaryjoin="""and_(Dialaction.action == 'voicemail',
                                                 Dialaction.actionarg1 == cast(Voicemail.id, String))""",
                             foreign_keys='Dialaction.actionarg1',
                             viewonly=True)

    incall = relationship('Incall',
                          primaryjoin="""and_(Dialaction.category == 'incall',
                                              Dialaction.categoryval == cast(Incall.id, String))""",
                          foreign_keys='Dialaction.categoryval',
                          viewonly=True,
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
        return self.action.split(':', 1)[0] if self.action else self.action

    @type.expression
    def type(cls):
        return func.split_part(cls.action, ':', 1)

    @type.setter
    def type(self, value):
        type_ = value if value else ''
        subtype = self.subtype if self.subtype else ''
        self._set_action(type_, subtype)

    @hybrid_property
    def subtype(self):
        type_subtype = self.action.split(':', 1) if self.action else ''
        return type_subtype[1] if len(type_subtype) == 2 else None

    @subtype.expression
    def subtype(cls):
        return func.split_part(cls.action, ':', 2)

    @subtype.setter
    def subtype(self, value):
        type_ = self.type if self.type else ''
        subtype = value if value else ''
        self._set_action(type_, subtype)

    def _set_action(self, type_, subtype):
        subtype = ':{}'.format(subtype) if subtype else ''
        self.action = '{}{}'.format(type_, subtype)

    @property
    def gosub_args(self):
        if not self.linked:
            return 'none'
        return ','.join(item or '' for item in (self.action, self.actionarg1, self.actionarg2))
