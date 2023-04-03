# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Integer, Text

from xivo_dao.helpers.db_manager import Base


class PJSIPTransportOption(Base):

    __tablename__ = 'pjsip_transport_option'
    __table_args__ = (
        Index(
            'pjsip_transport_option__idx__pjsip_transport_uuid',
            'pjsip_transport_uuid',
        ),
    )

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    pjsip_transport_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('pjsip_transport.uuid', ondelete='CASCADE'),
        nullable=False,
    )
