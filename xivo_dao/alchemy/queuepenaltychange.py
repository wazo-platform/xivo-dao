# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, Enum

from xivo_dao.helpers.db_manager import Base


class QueuePenaltyChange(Base):
    __tablename__ = 'queuepenaltychange'
    __table_args__ = (PrimaryKeyConstraint('queuepenalty_id', 'seconds'),)

    queuepenalty_id = Column(Integer, nullable=False, autoincrement=False)
    seconds = Column(Integer, nullable=False, server_default='0', autoincrement=False)
    maxp_sign = Column(
        Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata)
    )
    maxp_value = Column(Integer)
    minp_sign = Column(
        Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata)
    )
    minp_value = Column(Integer)
