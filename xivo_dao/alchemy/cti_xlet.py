# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiXlet(Base):

    __tablename__ = 'cti_xlet'

    id = Column(Integer, primary_key=True)
    plugin_name = Column(String(40), nullable=False)
