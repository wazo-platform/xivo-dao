# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
from sqlalchemy.sql import case, cast, func, not_
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy.rightcallexten import RightCallExten
from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.exception import InputError


class RightCall(Base):

    __tablename__ = 'rightcall'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False, server_default='')
    passwd = Column(String(40), nullable=False, server_default='')
    authorization = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    rightcallextens = relationship(RightCallExten, cascade="all, delete-orphan")

    @hybrid_property
    def password(self):
        if self.passwd == '':
            return None
        return self.passwd

    @password.expression
    def password(cls):
        return func.nullif(cls.passwd, '')

    @password.setter
    def password(self, value):
        if value is None:
            self.passwd = ''
        else:
            self.passwd = value

    @hybrid_property
    def mode(self):
        if self.authorization == 1:
            return 'allow'
        else:
            return 'deny'

    @mode.expression
    def mode(cls):
        return case([(cls.authorization == 1, 'allow')], else_='deny')

    @mode.setter
    def mode(self, value):
        if value == 'allow':
            self.authorization = 1
        elif value == 'deny':
            self.authorization = 0
        else:
            raise InputError("cannot set mode to {}. Only 'allow' or 'deny' are authorized".format(value))

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0)

    @property
    def extensions(self):
        return [rightcallexten.exten for rightcallexten in self.rightcallextens]

    @extensions.setter
    def extensions(self, values):
        old_rightcallextens = {rightcallexten.exten: rightcallexten for rightcallexten in self.rightcallextens}
        self.rightcallextens = []
        for value in set(values):
            if value in old_rightcallextens:
                self.rightcallextens.append(old_rightcallextens[value])
            else:
                self.rightcallextens.append(RightCallExten(rightcallid=self.id, exten=value))
