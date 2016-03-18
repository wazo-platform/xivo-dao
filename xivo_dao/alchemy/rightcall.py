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
from sqlalchemy.sql import cast, func, not_
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy.rightcallexten import RightCallExten
from xivo_dao.helpers.db_manager import Base


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
        return self.authorization

    @mode.setter
    def mode(self, value):
        self.authorization = value

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
        self.rightcallextens = [RightCallExten(rightcallid=self.id, exten=value) for value in values]
