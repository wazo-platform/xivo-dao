# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Resolvconf(Base):

    __tablename__ = 'resolvconf'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('domain'),
    )

    id = Column(Integer, nullable=False)
    hostname = Column(String(63), nullable=False, server_default='xivo')
    domain = Column(String(255), nullable=False, server_default='')
    nameserver1 = Column(String(255))
    nameserver2 = Column(String(255))
    nameserver3 = Column(String(255))
    search = Column(String(255))
    description = Column(Text)
