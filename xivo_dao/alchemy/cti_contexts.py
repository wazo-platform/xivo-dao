# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class CtiContexts(Base):

    __tablename__ = 'cticontexts'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    directories = Column(Text, nullable=False)
    display = Column(Text, nullable=False)
    description = Column(Text)
    deletable = Column(Integer)
