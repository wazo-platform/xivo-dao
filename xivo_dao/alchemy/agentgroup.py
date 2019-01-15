# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AgentGroup(Base):

    __tablename__ = 'agentgroup'

    id = Column(Integer, primary_key=True)
    groupid = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False, server_default='')
    groups = Column(String(255), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    deleted = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
