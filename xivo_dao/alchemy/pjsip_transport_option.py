# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Integer, Text

from xivo_dao.helpers.db_manager import Base


class PJSIPTransportOption(Base):

    __tablename__ = 'pjsip_transport_option'

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    pjsip_transport_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('pjsip_transport.uuid', ondelete='CASCADE'),
        nullable=False,
    )
