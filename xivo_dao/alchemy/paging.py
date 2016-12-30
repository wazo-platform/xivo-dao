# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 The Wazo Authors  (see the AUTHORS file)
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

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.types import Integer, String, Text, Boolean

from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.helpers.db_manager import Base


class Paging(Base):

    __tablename__ = 'paging'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('number'),
    )

    id = Column(Integer, nullable=False)
    number = Column(String(32))
    name = Column(String(128))
    duplex = Column(Integer, nullable=False, server_default='0')
    ignore = Column(Integer, nullable=False, server_default='0')
    record = Column(Integer, nullable=False, server_default='0')
    quiet = Column(Integer, nullable=False, server_default='0')
    timeout = Column(Integer, nullable=True, server_default='30')
    announcement_file = Column(String(64))
    announcement_play = Column(Integer, nullable=False, server_default='0')
    announcement_caller = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    paging_members = relationship('PagingUser',
                                  primaryjoin="""and_(PagingUser.pagingid == Paging.id,
                                                      PagingUser.caller == 0)""",
                                  cascade='all, delete-orphan')

    members = association_proxy('paging_members', 'user',
                                creator=lambda _user: PagingUser(user=_user,
                                                                 caller=0))

    paging_callers = relationship('PagingUser',
                                  primaryjoin="""and_(PagingUser.pagingid == Paging.id,
                                                      PagingUser.caller == 1)""",
                                  cascade='all, delete-orphan')

    callers = association_proxy('paging_callers', 'user',
                                creator=lambda _user: PagingUser(user=_user,
                                                                 caller=1))

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0)

    @hybrid_property
    def duplex_bool(self):
        return self.duplex == 1

    @duplex_bool.expression
    def duplex_bool(cls):
        return cast(cls.duplex, Boolean)

    @duplex_bool.setter
    def duplex_bool(self, value):
        self.duplex = int(value)

    @hybrid_property
    def record_bool(self):
        return self.record == 1

    @record_bool.expression
    def record_bool(cls):
        return cast(cls.record, Boolean)

    @record_bool.setter
    def record_bool(self, value):
        self.record = int(value)

    @hybrid_property
    def ignore_forward(self):
        return self.ignore == 1

    @ignore_forward.expression
    def ignore_forward(cls):
        return cast(cls.ignore, Boolean)

    @ignore_forward.setter
    def ignore_forward(self, value):
        self.ignore = int(value)

    @hybrid_property
    def caller_notification(self):
        return self.quiet == 0

    @caller_notification.expression
    def caller_notification(cls):
        return not_(cast(cls.quiet, Boolean))

    @caller_notification.setter
    def caller_notification(self, value):
        self.quiet = int(value == 0)

    @hybrid_property
    def announce_caller(self):
        return self.announcement_caller == 0

    @announce_caller.expression
    def announce_caller(cls):
        return not_(cast(cls.announcement_caller, Boolean))

    @announce_caller.setter
    def announce_caller(self, value):
        self.announcement_caller = int(value == 0)

    @hybrid_property
    def announce_sound(self):
        return self.announcement_file

    @announce_sound.setter
    def announce_sound(self, value):
        self.announcement_play = int(value is not None)
        self.announcement_file = value
