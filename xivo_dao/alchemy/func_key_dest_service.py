# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestService(Base):

    DESTINATION_TYPE_ID = 5

    __tablename__ = 'func_key_dest_service'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'extension_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        ForeignKeyConstraint(['extension_id'],
                             ['extensions.id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="{}".format(DESTINATION_TYPE_ID))
    extension_id = Column(Integer)

    type = 'service'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    extension = relationship(Extension)

    def __init__(self, **kwargs):
        self.service = kwargs.pop('service', None)  # TODO improve with relationship
        super(FuncKeyDestService, self).__init__(**kwargs)

    def to_tuple(self):
        return (('service', self.service),)
