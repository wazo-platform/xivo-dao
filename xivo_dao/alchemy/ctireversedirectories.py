# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text

from xivo_dao.helpers.db_manager import Base


class CtiReverseDirectories(Base):

    __tablename__ = 'ctireversedirectories'

    id = Column(Integer, primary_key=True)
    directories = Column(Text, nullable=False)
