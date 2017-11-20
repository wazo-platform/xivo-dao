# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiService(Base):

    __tablename__ = 'cti_service'

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
