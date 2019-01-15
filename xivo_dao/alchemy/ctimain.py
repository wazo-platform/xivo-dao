# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiMain(Base):

    __tablename__ = 'ctimain'

    id = Column(Integer, primary_key=True)
    ctis_active = Column(Integer, nullable=False, server_default='1')
    tlscertfile = Column(String(128))
    tlsprivkeyfile = Column(String(128))
    context_separation = Column(Integer)
    live_reload_conf = Column(Integer)
