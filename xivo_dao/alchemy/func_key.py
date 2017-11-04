# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+


from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.func_key_type import FuncKeyType
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
from xivo_dao.helpers.db_manager import Base


class FuncKey(Base):

    __tablename__ = 'func_key'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('func_key_type.id'), nullable=False)
    destination_type_id = Column(Integer,
                                 ForeignKey('func_key_destination_type.id'),
                                 primary_key=True)

    func_key_type = relationship(FuncKeyType, foreign_keys=type_id)
    destination_type = relationship(FuncKeyDestinationType, foreign_keys=destination_type_id)

    @classmethod
    def new_for_user(cls):
        type_id = FuncKeyType.query_id('speeddial').as_scalar()
        destination_type_id = FuncKeyDestinationType.query_id('user').as_scalar()
        return cls(type_id=type_id, destination_type_id=destination_type_id)
