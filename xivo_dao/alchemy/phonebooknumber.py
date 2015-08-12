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

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.alchemy.phonebook import Phonebook
from xivo_dao.helpers.db_manager import Base


class PhonebookNumber(Base):

    __tablename__ = 'phonebooknumber'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('phonebookid',),
                             ('phonebook.id',),
                             ondelete='CASCADE'),
        Index('phonebooknumber__uidx__phonebookid_type', 'phonebookid', 'type', unique=True),
    )

    id = Column(Integer)
    phonebookid = Column(Integer, nullable=False)
    number = Column(String(40), nullable=False, server_default='')
    type = Column(Enum('home', 'office', 'mobile', 'fax', 'other',
                       name='phonebooknumber_type',
                       metadata=Base.metadata),
                  nullable=False)

    phonebook = relationship(Phonebook)
