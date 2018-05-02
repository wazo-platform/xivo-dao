# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestForward(Base):

    DESTINATION_TYPE_ID = 6

    __tablename__ = 'func_key_dest_forward'
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
    number = Column(String(40), nullable=True)

    type = 'forward'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    extension = relationship(Extension)

    def __init__(self, **kwargs):
        self.forward = kwargs.pop('forward', None)  # TODO improve with relationship
        super(FuncKeyDestForward, self).__init__(**kwargs)

    def to_tuple(self):
        return (
            ('exten', self.exten),
            ('forward', self.forward),
        )

    @hybrid_property
    def exten(self):
        return self.number

    @exten.setter
    def exten(self, value):
        self.number = value
