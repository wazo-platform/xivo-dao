# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, CheckConstraint, \
    ForeignKeyConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestGroup(Base):

    DESTINATION_TYPE_ID = 2

    __tablename__ = 'func_key_dest_group'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="{}".format(DESTINATION_TYPE_ID))
    group_id = Column(Integer, ForeignKey('groupfeatures.id'), primary_key=True)

    type = 'group'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    groupfeatures = relationship(GroupFeatures)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('group_id', self.group_id),
        )
        return tuple(sorted(parameters))
