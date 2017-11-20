# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class IAXCallNumberLimits(Base):

    __tablename__ = 'iaxcallnumberlimits'

    id = Column(Integer, primary_key=True)
    destination = Column(String(39), nullable=False)
    netmask = Column(String(39), nullable=False)
    calllimits = Column(Integer, nullable=False, server_default='0')
