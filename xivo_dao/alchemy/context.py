# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Context(Base):

    __tablename__ = 'context'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    name = Column(String(39), nullable=False)
    displayname = Column(String(128))
    entity = Column(String(64))
    contexttype = Column(String(40), nullable=False, server_default='internal')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    context_numbers_user = relationship('ContextNumbers',
                                        primaryjoin="""and_(
                                            ContextNumbers.type == 'user',
                                            ContextNumbers.context == Context.name)""",
                                        foreign_keys='ContextNumbers.context',
                                        cascade='all, delete-orphan')

    context_numbers_group = relationship('ContextNumbers',
                                         primaryjoin="""and_(
                                             ContextNumbers.type == 'group',
                                             ContextNumbers.context == Context.name)""",
                                         foreign_keys='ContextNumbers.context',
                                         cascade='all, delete-orphan')

    context_numbers_queue = relationship('ContextNumbers',
                                         primaryjoin="""and_(
                                             ContextNumbers.type == 'queue',
                                             ContextNumbers.context == Context.name)""",
                                         foreign_keys='ContextNumbers.context',
                                         cascade='all, delete-orphan')

    context_numbers_meetme = relationship('ContextNumbers',
                                          primaryjoin="""and_(
                                              ContextNumbers.type == 'meetme',
                                              ContextNumbers.context == Context.name)""",
                                          foreign_keys='ContextNumbers.context',
                                          cascade='all, delete-orphan')

    context_numbers_incall = relationship('ContextNumbers',
                                          primaryjoin="""and_(
                                              ContextNumbers.type == 'incall',
                                              ContextNumbers.context == Context.name)""",
                                          foreign_keys='ContextNumbers.context',
                                          cascade='all, delete-orphan')

    @hybrid_property
    def label(self):
        return self.displayname

    @label.setter
    def label(self, value):
        self.displayname = value

    @hybrid_property
    def type(self):
        return self.contexttype

    @type.setter
    def type(self, value):
        self.contexttype = value

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
    def user_ranges(self):
        return self.context_numbers_user

    @user_ranges.setter
    def user_ranges(self, user_ranges):
        for user_range in user_ranges:
            user_range.type = 'user'
        self.context_numbers_user = user_ranges

    @hybrid_property
    def group_ranges(self):
        return self.context_numbers_group

    @group_ranges.setter
    def group_ranges(self, group_ranges):
        for group_range in group_ranges:
            group_range.type = 'group'
        self.context_numbers_group = group_ranges

    @hybrid_property
    def queue_ranges(self):
        return self.context_numbers_queue

    @queue_ranges.setter
    def queue_ranges(self, queue_ranges):
        for queue_range in queue_ranges:
            queue_range.type = 'queue'
        self.context_numbers_queue = queue_ranges

    @hybrid_property
    def meetme_ranges(self):
        return self.context_numbers_meetme

    @meetme_ranges.setter
    def meetme_ranges(self, meetme_ranges):
        for meetme_range in meetme_ranges:
            meetme_range.type = 'meetme'
        self.context_numbers_meetme = meetme_ranges

    @hybrid_property
    def incall_ranges(self):
        return self.context_numbers_incall

    @incall_ranges.setter
    def incall_ranges(self, incall_ranges):
        for incall_range in incall_ranges:
            incall_range.type = 'incall'
        self.context_numbers_incall = incall_ranges
