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
from sqlalchemy.schema import Column
from sqlalchemy.sql import case
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class ContextNumbers(Base):

    __tablename__ = 'contextnumbers'

    context = Column(String(39), primary_key=True)
    type = Column(Enum('user', 'group', 'queue', 'meetme', 'incall',
                       name='contextnumbers_type',
                       metadata=Base.metadata),
                  primary_key=True)
    numberbeg = Column(String(16), server_default='', primary_key=True)
    numberend = Column(String(16), server_default='', primary_key=True)
    didlength = Column(Integer, nullable=False, server_default='0')

    @hybrid_property
    def start(self):
        return self.numberbeg

    @start.setter
    def start(self, value):
        self.numberbeg = value

    @hybrid_property
    def end(self):
        if self.numberend == '':
            return self.numberbeg
        return self.numberend

    @end.expression
    def end(cls):
        return case([(cls.numberend == '', cls.numberbeg)], else_=cls.numberend)

    @end.setter
    def end(self, value):
        self.numberend = value

    @hybrid_property
    def did_length(self):
        return self.didlength

    @did_length.setter
    def did_length(self, value):
        self.didlength = value

    def in_range(self, exten):
        exten = int(exten)
        start = self._convert_limit(self.start)
        end = self._convert_limit(self.end)

        if start == end and exten == start:
            return True
        elif start <= exten <= end:
            return True
        return False

    def _convert_limit(self, limit):
        return int(limit[-self.did_length:])
