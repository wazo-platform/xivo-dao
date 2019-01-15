# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, UniqueConstraint, CheckConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AccessFeatures(Base):

    __tablename__ = 'accessfeatures'
    __table_args__ = (
        CheckConstraint('feature=\'phonebook\''),
        UniqueConstraint('host', 'feature'),
    )

    id = Column(Integer, primary_key=True)
    host = Column(String(255), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    feature = Column(String(64), nullable=False, server_default='phonebook')
