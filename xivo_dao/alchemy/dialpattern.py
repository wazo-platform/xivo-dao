# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class DialPattern(Base):

    __tablename__ = 'dialpattern'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    type = Column(String(32), nullable=False)
    typeid = Column(Integer, nullable=False)
    externprefix = Column(String(64))
    prefix = Column(String(32))
    exten = Column(String(40), nullable=False)
    stripnum = Column(Integer)
    callerid = Column(String(80))

    @hybrid_property
    def external_prefix(self):
        return self.externprefix

    @external_prefix.setter
    def external_prefix(self, value):
        self.externprefix = value

    @hybrid_property
    def pattern(self):
        return self.exten

    @pattern.setter
    def pattern(self, value):
        self.exten = value

    @hybrid_property
    def strip_digits(self):
        return self.stripnum

    @strip_digits.setter
    def strip_digits(self, value):
        if value is None:
            value = 0  # set default value
        self.stripnum = value

    @hybrid_property
    def caller_id(self):
        return self.callerid

    @caller_id.setter
    def caller_id(self, value):
        self.callerid = value
