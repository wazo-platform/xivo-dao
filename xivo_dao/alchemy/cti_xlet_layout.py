# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiXletLayout(Base):

    __tablename__ = 'cti_xlet_layout'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
