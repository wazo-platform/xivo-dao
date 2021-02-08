# -*- coding: utf-8 -*-
# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Index
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case, select

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid

from .call_log import CallLog


class CallLogParticipant(Base):

    __tablename__ = 'call_log_participant'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        Index('call_log_participant__idx__user_uuid', 'user_uuid'),
    )

    uuid = Column(String(38), default=new_uuid)
    call_log_id = Column(Integer, ForeignKey('call_log.id', name='fk_call_log_id', ondelete='CASCADE'))
    user_uuid = Column(String(38), nullable=False)
    line_id = Column(Integer)
    role = Column('role', Enum('source', 'destination', name='call_log_participant_role'), nullable=False)
    tags = Column(ARRAY(String(128)), nullable=False, server_default='{}')
    answered = Column(Boolean, nullable=False, server_default='false')

    call_log = relationship(
        'CallLog',
        primaryjoin='CallLog.id == CallLogParticipant.call_log_id',
        uselist=False,
    )

    @hybrid_property
    def peer_exten(self):
        if self.role == 'source':
            return self.call_log.requested_exten
        else:
            return self.call_log.source_exten

    @peer_exten.expression
    def peer_exten(cls):
        return case(
            [
                (
                    cls.role == 'source',
                    select([CallLog.requested_exten]).where(
                        cls.call_log_id == CallLog.id
                    ).as_scalar()
                )
            ],
            else_=select([CallLog.source_exten]).where(
                cls.call_log_id == CallLog.id
            ).as_scalar()
        )
