# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, CheckConstraint, \
    ForeignKeyConstraint
from sqlalchemy.types import Integer, Boolean, String
from sqlalchemy.orm import relationship

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
