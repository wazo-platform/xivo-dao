# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class SCCPDevice(Base):

    __tablename__ = 'sccpdevice'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    device = Column(String(80), nullable=False)
    line = Column(String(80), nullable=False, server_default='')
