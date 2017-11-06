# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AgentFeatures(Base):

    __tablename__ = 'agentfeatures'
    __table_args__ = (
        UniqueConstraint('number'),
    )

    id = Column(Integer, primary_key=True)
    numgroup = Column(Integer, nullable=False)
    firstname = Column(String(128), nullable=False, server_default='')
    lastname = Column(String(128), nullable=False, server_default='')
    number = Column(String(40), nullable=False)
    passwd = Column(String(128), nullable=False)
    context = Column(String(39), nullable=False)
    language = Column(String(20), nullable=False)
    autologoff = Column(Integer)
    group = Column(String(255))
    description = Column(Text, nullable=False)
    preprocess_subroutine = Column(String(40))
