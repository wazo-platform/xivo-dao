# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String


class FuncKeyDestCustom(Base):

    DESTINATION_TYPE_ID = 10

    __tablename__ = 'func_key_dest_custom'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="{}".format(DESTINATION_TYPE_ID))
    exten = Column(String(40), nullable=False)

    type = 'custom'  # TODO improve with relationship

    func_key = relationship(FuncKey)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('exten', self.exten),
        )
        return tuple(sorted(parameters))
