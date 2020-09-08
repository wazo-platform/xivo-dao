# -*- coding: utf-8 -*-
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    Index,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.types import (
    Boolean,
    Integer,
    String,
    Text,
)

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk


class TrunkFeatures(Base):

    __tablename__ = 'trunkfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        CheckConstraint(
            '''
            ( CASE WHEN endpoint_sip_uuid IS NULL THEN 0 ELSE 1 END
            + CASE WHEN endpoint_iax_id IS NULL THEN 0 ELSE 1 END
            + CASE WHEN endpoint_custom_id IS NULL THEN 0 ELSE 1 END
            ) <= 1
            ''',
            name='trunkfeatures_endpoints_check',
        ),
        CheckConstraint(
            '''
            (
                register_iax_id IS NULL
            ) OR (
                register_iax_id IS NOT NULL AND
                endpoint_sip_uuid IS NULL AND
                endpoint_custom_id IS NULL
            )
            ''',
            name='trunkfeatures_endpoint_register_check',
        ),
        Index('trunkfeatures__idx__registercommented', 'registercommented'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    endpoint_sip_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='SET NULL'),
    )
    endpoint_iax_id = Column(Integer, ForeignKey('useriax.id', ondelete='SET NULL'))
    endpoint_custom_id = Column(Integer, ForeignKey('usercustom.id', ondelete='SET NULL'))
    register_iax_id = Column(Integer, ForeignKey('staticiax.id', ondelete='SET NULL'))
    registercommented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    context = Column(String(39))
    twilio_incoming = Column(Boolean, nullable=False, server_default='False')

    endpoint_sip = relationship('EndpointSIP', viewonly=True)
    endpoint_iax = relationship('UserIAX', viewonly=True)
    endpoint_custom = relationship('UserCustom', viewonly=True)

    context_rel = relationship(
        'Context',
        primaryjoin='TrunkFeatures.context == Context.name',
        foreign_keys='TrunkFeatures.context',
        viewonly=True,
    )

    outcall_trunks = relationship(
        'OutcallTrunk',
        cascade='all, delete-orphan',
        back_populates='trunk',
    )

    outcalls = association_proxy(
        'outcall_trunks', 'outcall',
        creator=lambda _outcall: OutcallTrunk(outcall=_outcall),
    )

    register_iax = relationship('StaticIAX', viewonly=True)

    @property
    def protocol(self):
        if self.endpoint_sip_uuid:
            return 'sip'
        elif self.endpoint_iax_id:
            return 'iax'
        elif self.endpoint_custom_id:
            return 'custom'

        if self.register_iax_id:
            return 'iax'
