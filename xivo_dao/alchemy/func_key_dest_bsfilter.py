# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from sqlalchemy.ext.hybrid import hybrid_property
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer


class FuncKeyDestBSFilter(Base):

    __tablename__ = 'func_key_dest_bsfilter'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'filtermember_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        ForeignKeyConstraint(['filtermember_id'],
                             ['callfiltermember.id']),
        CheckConstraint('destination_type_id = 12')
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="12")
    filtermember_id = Column(Integer, nullable=False)

    type = 'bsfilter'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    filtermember = relationship(Callfiltermember)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('filter_member_id', self.filtermember_id),
        )
        return tuple(sorted(parameters))

    @hybrid_property
    def filter_member_id(self):
        return self.filtermember_id

    @filter_member_id.setter
    def filter_member_id(self, value):
        self.filtermember_id = value
