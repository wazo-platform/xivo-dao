# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AgentGlobalParams(Base):
    __tablename__ = 'agentglobalparams'

    id = Column(Integer, primary_key=True)
    category = Column(String(128), nullable=False)
    option_name = Column(String(255), nullable=False)
    option_value = Column(String(255))
