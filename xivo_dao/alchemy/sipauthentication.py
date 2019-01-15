# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Enum


class SIPAuthentication(Base):

    __tablename__ = 'sipauthentication'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('sipauthentication__idx__usersip_id', 'usersip_id')
    )

    id = Column(Integer, nullable=False)
    usersip_id = Column(Integer)
    user = Column(String(255), nullable=False)
    secretmode = Column(Enum('md5',
                             'clear',
                             name='sipauthentication_secretmode',
                             metadata=Base.metadata), nullable=False)
    secret = Column(String(255), nullable=False)
    realm = Column(String(1024), nullable=False)
