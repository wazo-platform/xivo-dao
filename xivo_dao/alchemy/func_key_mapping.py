# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, Boolean, String

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.helpers.db_manager import Base


class FuncKeyMapping(Base):

    __tablename__ = 'func_key_mapping'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        UniqueConstraint('template_id', 'position'),
        CheckConstraint('position > 0')
    )

    template_id = Column(Integer, ForeignKey('func_key_template.id'), primary_key=True)
    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True)
    label = Column(String(128))
    position = Column(Integer, nullable=False)
    blf = Column(Boolean, nullable=False, server_default='True')

    func_key_template = relationship(FuncKeyTemplate)
    func_key = relationship(FuncKey)

    def __init__(self, **kwargs):
        self.destination = kwargs.pop('destination', None)  # TODO improve with relationship
        self.inherited = kwargs.pop('inherited', True)  # TODO improve ...
        kwargs.setdefault('blf', True)  # TODO improve this ugly init
        super(FuncKeyMapping, self).__init__(**kwargs)

    @hybrid_property
    def id(self):
        return self.func_key_id

    @id.setter
    def id(self, value):
        self.func_key_id = value

    def hash_destination(self):
        if self.destination:
            return self.destination.to_tuple()
        return None
