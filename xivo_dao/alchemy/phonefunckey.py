# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class PhoneFunckey(Base):

    __tablename__ = 'phonefunckey'
    __table_args__ = (
        PrimaryKeyConstraint('iduserfeatures', 'fknum'),
        Index('phonefunckey__idx__exten', 'exten'),
        Index('phonefunckey__idx__progfunckey', 'progfunckey'),
        Index('phonefunckey__idx__typeextenumbers_typevalextenumbers', 'typeextenumbers', 'typevalextenumbers'),
        Index('phonefunckey__idx__typeextenumbersright_typevalextenumbersright', 'typeextenumbersright', 'typevalextenumbersright'),
    )

    iduserfeatures = Column(Integer, nullable=False, autoincrement=False)
    fknum = Column(Integer, nullable=False, autoincrement=False)
    exten = Column(String(40))
    typeextenumbers = Column(String(255))
    typevalextenumbers = Column(Enum('extenfeatures', 'featuremap', 'generalfeatures',
                                     name='phonefunckey_typeextenumbers',
                                     metadata=Base.metadata))
    typeextenumbersright = Column(String(255))
    typevalextenumbersright = Column(Enum('agent', 'group', 'meetme', 'queue', 'user', 'paging',
                                          name='phonefunckey_typeextenumbersright',
                                          metadata=Base.metadata))
    label = Column(String(32))
    supervision = Column(Integer, nullable=False, server_default='0')
    progfunckey = Column(Integer, nullable=False, server_default='0')
