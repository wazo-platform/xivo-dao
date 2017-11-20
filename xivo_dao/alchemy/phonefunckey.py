# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class PhoneFunckey(Base):

    __tablename__ = 'phonefunckey'
    __table_args__ = (
        PrimaryKeyConstraint('iduserfeatures', 'fknum'),
        Index('phonefunckey__idx__exten', 'exten'),
        Index('phonefunckey__idx__progfunckey', 'progfunckey'),
        Index('phonefunckey__idx__typeextenumbers_typevalextenumbers', 'typeextenumbers', 'typevalextenumbers'),
        Index('phonefunckey__idx__typeextenumbersright_typevalextenumbersright', 'typeextenumbersright', 'typevalextenumbersright'),
    )

    iduserfeatures = Column(Integer, nullable=False, autoincrement=False)
    fknum = Column(Integer, nullable=False, autoincrement=False)
    exten = Column(String(40))
    typeextenumbers = Column(Enum('extenfeatures', 'featuremap', 'generalfeatures',
                                  name='phonefunckey_typeextenumbers',
                                  metadata=Base.metadata))
    typevalextenumbers = Column(String(255))
    typeextenumbersright = Column(Enum('agent', 'group', 'meetme', 'queue', 'user', 'paging',
                                       name='phonefunckey_typeextenumbersright',
                                       metadata=Base.metadata))
    typevalextenumbersright = Column(String(255))
    label = Column(String(32))
    supervision = Column(Integer, nullable=False, server_default='0')
    progfunckey = Column(Integer, nullable=False, server_default='0')
