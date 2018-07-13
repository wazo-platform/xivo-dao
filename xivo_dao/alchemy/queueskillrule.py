# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class QueueSkillRule(Base):

    __tablename__ = 'queueskillrule'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    rule = Column(Text)
