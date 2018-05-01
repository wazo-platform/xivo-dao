# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestFeatures(Base):

    __tablename__ = 'func_key_dest_features'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'features_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        ForeignKeyConstraint(['features_id'],
                             ['features.id']),
        CheckConstraint('destination_type_id = 8')
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="8")
    features_id = Column(Integer)

    type = 'transfer'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    features = relationship(Features)

    def __init__(self, **kwargs):
        self.transfer = kwargs.pop('transfer', None)  # TODO improve with relationship
        super(FuncKeyDestFeatures, self).__init__(**kwargs)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('transfer', self.transfer),
        )
        return parameters

    @hybrid_property
    def feature_id(self):
        return self.features_id

    @feature_id.setter
    def feature_id(self, value):
        self.features_id = value
