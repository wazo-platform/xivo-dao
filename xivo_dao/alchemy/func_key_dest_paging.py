# -*- coding: utf-8 -*-

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

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.paging import Paging
from xivo_dao.helpers.db_manager import Base

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer


class FuncKeyDestPaging(Base):

    __tablename__ = 'func_key_dest_paging'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'paging_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        ForeignKeyConstraint(['paging_id'],
                             ['paging.id']),
        CheckConstraint('destination_type_id = 9')
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="9")
    paging_id = Column(Integer)

    func_key = relationship(FuncKey)
    paging = relationship(Paging)
