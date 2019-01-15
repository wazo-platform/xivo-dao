# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class CtiSheetActions(Base):

    __tablename__ = 'ctisheetactions'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text, nullable=False)
    whom = Column(String(50))
    sheet_info = Column(Text)
    systray_info = Column(Text)
    sheet_qtui = Column(Text)
    action_info = Column(Text)
    focus = Column(Integer)
    deletable = Column(Integer)
    disable = Column(Integer)
