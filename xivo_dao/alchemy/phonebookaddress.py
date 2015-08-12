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


class PhonebookAddress(Base):

    __tablename__ = 'phonebookaddress'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('phonebookid',),
                             ('phonebook.id',),
                             ondelete='CASCADE'),
        Index('phonebookaddress__uidx__phonebookid_type', 'phonebookid', 'type', unique=True),
    )

    id = Column(Integer)
    phonebookid = Column(Integer, nullable=False)
    address1 = Column(String(30), nullable=False, server_default='')
    address2 = Column(String(30), nullable=False, server_default='')
    city = Column(String(128), nullable=False, server_default='')
    state = Column(String(128), nullable=False, server_default='')
    zipcode = Column(String(16), nullable=False, server_default='')
    country = Column(String(3), nullable=False, server_default='')
    type = Column(Enum('home', 'office', 'other',
                       name='phonebookaddress_type',
                       metadata=Base.metadata),
                  nullable=False)

    phonebook = relationship(Phonebook)
