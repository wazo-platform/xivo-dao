# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, CheckConstraint
from sqlalchemy.types import DateTime, Integer, String

from xivo_dao.alchemy.cel import CEL
from xivo_dao.helpers.db_manager import Base


class CallLog(Base):

    __tablename__ = 'call_log'

    id = Column(Integer, nullable=False, primary_key=True)
    date = Column(DateTime, nullable=False)
    date_answer = Column(DateTime)
    date_end = Column(DateTime)
    source_name = Column(String(255))
    source_exten = Column(String(255))
    source_line_identity = Column(String(255))
    destination_name = Column(String(255))
    destination_exten = Column(String(255))
    destination_line_identity = Column(String(255))
    direction = Column(String(255))
    user_field = Column(String(255))
    participants = relationship('CallLogParticipant',
                                cascade='all,delete-orphan')
    participant_user_uuids = association_proxy('participants', 'user_uuid')

    cels = relationship(CEL)

    cel_ids = []

    __table_args__ = (
        CheckConstraint(direction.in_(['inbound', 'internal', 'outbound']),
                        name='call_log_direction_check'),
    )
