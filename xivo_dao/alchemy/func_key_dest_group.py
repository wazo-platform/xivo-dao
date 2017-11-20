# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, CheckConstraint, \
    ForeignKeyConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestGroup(Base):

    __tablename__ = 'func_key_dest_group'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id=2'),
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="2")
    group_id = Column(Integer, ForeignKey('groupfeatures.id'), primary_key=True)

    func_key = relationship(FuncKey)
    groupfeatures = relationship(GroupFeatures)
