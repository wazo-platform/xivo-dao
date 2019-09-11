# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, CheckConstraint
from sqlalchemy.types import DateTime, Integer, String, Text

from xivo_dao.alchemy.cel import CEL
from xivo_dao.helpers.db_manager import Base


class CallLog(Base):

    __tablename__ = 'call_log'

    id = Column(Integer, nullable=False, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False)
    date_answer = Column(DateTime(timezone=True))
    date_end = Column(DateTime(timezone=True))
    tenant_uuid = Column(String(36), nullable=False)
    source_name = Column(String(255))
    source_exten = Column(String(255))
    source_internal_exten = Column(Text)
    source_internal_context = Column(Text)
    source_line_identity = Column(String(255))
    requested_exten = Column(String(255))
    requested_context = Column(String(255))
    requested_internal_exten = Column(Text)
    requested_internal_context = Column(Text)
    destination_name = Column(String(255))
    destination_exten = Column(String(255))
    destination_internal_exten = Column(Text)
    destination_internal_context = Column(Text)
    destination_line_identity = Column(String(255))
    direction = Column(String(255))
    user_field = Column(String(255))
    participants = relationship('CallLogParticipant',
                                cascade='all,delete-orphan')
    participant_user_uuids = association_proxy('participants', 'user_uuid')
    source_participant = relationship('CallLogParticipant',
                                      primaryjoin='''and_(CallLogParticipant.call_log_id == CallLog.id,
                                                          CallLogParticipant.role == 'source')''',
                                      viewonly=True,
                                      uselist=False)
    source_user_uuid = association_proxy('source_participant', 'user_uuid')
    source_line_id = association_proxy('source_participant', 'line_id')
    destination_participant = relationship('CallLogParticipant',
                                           primaryjoin='''and_(CallLogParticipant.call_log_id == CallLog.id,
                                                               CallLogParticipant.role == 'destination')''',
                                           viewonly=True,
                                           uselist=False)
    destination_user_uuid = association_proxy('destination_participant', 'user_uuid')
    destination_line_id = association_proxy('destination_participant', 'line_id')

    cels = relationship(CEL)

    cel_ids = []

    __table_args__ = (
        CheckConstraint(direction.in_(['inbound', 'internal', 'outbound']),
                        name='call_log_direction_check'),
    )
