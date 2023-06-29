# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, Enum

from xivo_dao.helpers.db_manager import Base


class QueuePenaltyChange(Base):

    __tablename__ = 'queuepenaltychange'
    __table_args__ = (
        PrimaryKeyConstraint('queuepenalty_id', 'seconds'),
        {
            'comment': 'Contains rules to change penalties dynamically. '
                       'A rule changes the values of the Asterisk '
                       'QUEUE_MIN_PENALTY and QUEUE_MAX_PENALTY channel '
                       'variables.'
        }
    )

    queuepenalty_id = Column(Integer, nullable=False, autoincrement=False)
    seconds = Column(Integer, nullable=False, server_default='0', autoincrement=False, comment=' number of seconds to wait before changing the penalty values')
    maxp_sign = Column(Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata))
    maxp_value = Column(Integer, comment='maximum queue member penalty that could be used')
    minp_sign = Column(Enum('=', '+', '-', name='queuepenaltychange_sign', metadata=Base.metadata))
    minp_value = Column(Integer, comment='minimum queue member penalty to be used')
