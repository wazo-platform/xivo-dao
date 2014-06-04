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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.alchemy import enum
from xivo_dao.helpers.db_manager import Base
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import text


class Callfilter(Base):

    __tablename__ = 'callfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             name='fk_entity_id',
                             ondelete='RESTRICT'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    entity_id = Column(Integer, server_default=text('NULL'))
    name = Column(String(128), nullable=False, server_default='')
    type = Column(enum.callfilter_type, nullable=False)
    bosssecretary = Column(enum.callfilter_bosssecretary)
    callfrom = Column(enum.callfilter_callfrom)
    ringseconds = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)

    entity = relationship('Entity')
