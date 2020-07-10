# -*- coding: utf-8 -*-
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
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
