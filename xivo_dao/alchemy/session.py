# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Session(Base):

    __tablename__ = 'session'
    __table_args__ = (
        PrimaryKeyConstraint('sessid'),
        Index('session__idx__expire', 'expire'),
        Index('session__idx__identifier', 'identifier'),
    )

    sessid = Column(String(32), nullable=False)
    start = Column(Integer, nullable=False)
    expire = Column(Integer, nullable=False)
    identifier = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)
