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

from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AgentFeatures(Base):

    __tablename__ = 'agentfeatures'
    __table_args__ = (
        UniqueConstraint('number'),
    )

    id = Column(Integer, primary_key=True)
    numgroup = Column(Integer, nullable=False)
    firstname = Column(String(128), nullable=False, server_default='')
    lastname = Column(String(128), nullable=False, server_default='')
    number = Column(String(40), nullable=False)
    passwd = Column(String(128), nullable=False)
    context = Column(String(39), nullable=False)
    language = Column(String(20), nullable=False)
    autologoff = Column(Integer)
    group = Column(String(255))
    description = Column(Text, nullable=False)
    preprocess_subroutine = Column(String(40))
