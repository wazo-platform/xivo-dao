# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, String

from xivo_dao.helpers.db_manager import Base


class CtiDirectories(Base):

    __tablename__ = 'ctidirectories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    delimiter = Column(String(20))
    match_direct = Column(Text, nullable=False)
    match_reverse = Column(Text, nullable=False, default='')
    description = Column(String(255))
    deletable = Column(Integer)
    directory_id = Column(Integer, ForeignKey('directories.id', ondelete='CASCADE'))
