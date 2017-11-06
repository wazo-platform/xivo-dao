# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Boolean, String

from xivo_dao.helpers.db_manager import Base


class FuncKeyTemplate(Base):

    __tablename__ = 'func_key_template'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=True)
    private = Column(Boolean, nullable=False, server_default='False')
