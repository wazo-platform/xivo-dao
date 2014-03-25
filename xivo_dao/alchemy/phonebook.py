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

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text, Enum, LargeBinary

from xivo_dao.helpers.db_manager import Base


class Phonebook(Base):

    __tablename__ = 'phonebook'

    id = Column(Integer, primary_key=True)
    title = Column(Enum('mr', 'mrs', 'ms',
                        name='phonebook_title',
                        metadata=Base.metadata),
                   nullable=False)
    firstname = Column(String(128), nullable=False, server_default='')
    lastname = Column(String(128), nullable=False, server_default='')
    displayname = Column(String(64), nullable=False, server_default='')
    society = Column(String(128), nullable=False, server_default='')
    email = Column(String(255), nullable=False, server_default='')
    url = Column(String(255), nullable=False, server_default='')
    image = Column(LargeBinary)
    description = Column(Text, nullable=False)
