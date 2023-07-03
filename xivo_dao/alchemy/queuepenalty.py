# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class QueuePenalty(Base):

    __tablename__ = 'queuepenalty'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    name = Column(String(255), nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)
