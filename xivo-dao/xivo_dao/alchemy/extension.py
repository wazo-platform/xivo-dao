# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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


from xivo_dao.helpers.db_manager import Base, Type
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Enum


class Extension(Base):
    __tablename__ = 'extensions'
    __table_args__ = UniqueConstraint('exten', 'context')

    id = Column(Integer, primary_key=True)
    commented = Column(Integer)
    context = Column(String(39), nullable=False, server_default='')
    exten = Column(String(40), nullable=False, server_default='')
    type = Column(Enum('extenfeatures',
                       'featuremap',
                       'generalfeatures',
                       'group',
                       'incall',
                       'meetme',
                       'outcall',
                       'queue',
                       'user',
                       name='extenumbers_type',
                       metadata=Type.metadata),
                    nullable=False)
    typeval = Column(String(255))

    @property
    def name(self):
        return self.typeval
