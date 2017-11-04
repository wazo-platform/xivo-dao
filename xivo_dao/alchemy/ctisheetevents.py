# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiSheetEvents(Base):

    __tablename__ = 'ctisheetevents'

    id = Column(Integer, primary_key=True)
    incomingdid = Column(String(50))
    hangup = Column(String(50))
    dial = Column(String(50))
    link = Column(String(50))
    unlink = Column(String(50))
