# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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
from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint,\
    UniqueConstraint
from sqlalchemy.types import Integer, String, Enum, Text

from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base


class User(Base):

    __tablename__ = 'user'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('login', 'meta'),
    )

    id = Column(Integer, nullable=False)
    entity_id = Column(Integer)
    login = Column(String(64), nullable=False, server_default='')
    passwd = Column(String(64), nullable=False, server_default='')
    meta = Column(Enum('user',
                       'admin',
                       'root',
                       name='user_meta',
                       metadata=Base.metadata),
                  nullable=False, server_default='user')
    valid = Column(Integer, nullable=False, server_default='1')
    time = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    dupdate = Column(Integer, nullable=False, server_default='0')
    obj = Column(Text, nullable=False)

    entity = relationship(Entity)
