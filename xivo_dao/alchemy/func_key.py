# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base

from .func_key_destination_type import FuncKeyDestinationType
from .func_key_type import FuncKeyType


class FuncKey(Base):

    __tablename__ = 'func_key'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('func_key_type.id'), nullable=False)
    destination_type_id = Column(Integer,
                                 ForeignKey('func_key_destination_type.id'),
                                 primary_key=True)

    func_key_type = relationship(FuncKeyType, foreign_keys=type_id)
    destination_type = relationship(FuncKeyDestinationType, foreign_keys=destination_type_id, viewonly=True)
    destination_type_name = association_proxy('destination_type', 'name')

    func_key_mapping = relationship('FuncKeyMapping', cascade='all,delete-orphan')
