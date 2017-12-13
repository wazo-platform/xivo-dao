# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AsteriskFile(Base):

    __tablename__ = 'asterisk_file'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
