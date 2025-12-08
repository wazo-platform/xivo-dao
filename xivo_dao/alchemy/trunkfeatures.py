# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import case, select
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .endpoint_sip import EndpointSIP
from .outcalltrunk import OutcallTrunk
from .usercustom import UserCustom
from .useriax import UserIAX


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
        Index('trunkfeatures__idx__tenant_uuid', 'tenant_uuid'),
        Index('trunkfeatures__idx__endpoint_sip_uuid', 'endpoint_sip_uuid'),
        Index('trunkfeatures__idx__endpoint_iax_id', 'endpoint_iax_id'),
        Index('trunkfeatures__idx__endpoint_custom_id', 'endpoint_custom_id'),
        Index('trunkfeatures__idx__register_iax_id', 'register_iax_id'),
        Index('trunkfeatures__idx__registercommented', 'registercommented'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    endpoint_sip_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='SET NULL'),
    )
    endpoint_iax_id = Column(Integer, ForeignKey('useriax.id', ondelete='SET NULL'))
    endpoint_custom_id = Column(
        Integer, ForeignKey('usercustom.id', ondelete='SET NULL')
    )
    register_iax_id = Column(Integer, ForeignKey('staticiax.id', ondelete='SET NULL'))
    registercommented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    context = Column(String(79))
    outgoing_caller_id_format = Column(
        Text,
        CheckConstraint("outgoing_caller_id_format in ('+E164', 'E164', 'national')"),
        nullable=False,
        server_default='+E164',
    )
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
        'outcall_trunks',
        'outcall',
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

    @hybrid_property
    def name(self):
        if self.endpoint_sip and self.endpoint_sip.name not in ("", None):
            return self.endpoint_sip.name
        elif self.endpoint_iax and self.endpoint_iax.name not in ("", None):
            return self.endpoint_iax.name
        elif self.endpoint_custom and self.endpoint_custom.interface not in ("", None):
            return self.endpoint_custom.interface
        return None

    @name.expression
    def name(cls):
        endpoint_sip_query = (
            select(EndpointSIP.name)
            .where(EndpointSIP.uuid == cls.endpoint_sip_uuid)
            .scalar_subquery()
        )
        endpoint_iax_query = (
            select(UserIAX.name)
            .where(UserIAX.id == cls.endpoint_iax_id)
            .scalar_subquery()
        )  # fmt: skip
        endpoint_custom_query = (
            select(UserCustom.interface)
            .where(UserCustom.id == cls.endpoint_custom_id)
            .scalar_subquery()
        )
        return case(
            (cls.endpoint_sip_uuid.isnot(None), endpoint_sip_query),
            (cls.endpoint_iax_id.isnot(None), endpoint_iax_query),
            (cls.endpoint_custom_id.isnot(None), endpoint_custom_query),
            else_=None,
        )

    @hybrid_property
    def label(self):
        if self.endpoint_sip and self.endpoint_sip.label not in ("", None):
            return self.endpoint_sip.label
        return None

    @label.expression
    def label(cls):
        endpoint_sip_query = (
            select(EndpointSIP.label)
            .where(EndpointSIP.uuid == cls.endpoint_sip_uuid)
            .scalar_subquery()
        )
        return case(
            (cls.endpoint_sip_uuid.isnot(None), endpoint_sip_query),
            else_=None,
        )
