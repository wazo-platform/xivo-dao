# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, Index
from sqlalchemy.types import Boolean, Integer, Text, String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk


class TrunkFeatures(Base):

    __tablename__ = 'trunkfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('protocol', 'protocolid'),
        Index('trunkfeatures__idx__registercommented', 'registercommented'),
        Index('trunkfeatures__idx__registerid', 'registerid')
    )

    id = Column(Integer, nullable=False)
    protocol = Column(enum.trunk_protocol)
    protocolid = Column(Integer)
    registerid = Column(Integer, nullable=False, server_default='0')
    registercommented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    context = Column(String(39))
    twilio_incoming = Column(Boolean, nullable=False, server_default='False')

    endpoint_sip = relationship('UserSIP',
                                primaryjoin="""and_(
                                    TrunkFeatures.protocol == 'sip',
                                    TrunkFeatures.protocolid == UserSIP.id
                                )""",
                                foreign_keys='TrunkFeatures.protocolid',
                                viewonly=True,
                                back_populates='trunk')

    endpoint_iax = relationship('UserIAX',
                                primaryjoin="""and_(
                                    TrunkFeatures.protocol == 'iax',
                                    TrunkFeatures.protocolid == UserIAX.id
                                )""",
                                foreign_keys='TrunkFeatures.protocolid',
                                viewonly=True,
                                back_populates='trunk_rel')

    endpoint_custom = relationship('UserCustom',
                                   primaryjoin="""and_(
                                       TrunkFeatures.protocol == 'custom',
                                       TrunkFeatures.protocolid == UserCustom.id
                                   )""",
                                   foreign_keys='TrunkFeatures.protocolid',
                                   viewonly=True,
                                   back_populates='trunk')

    outcall_trunks = relationship('OutcallTrunk',
                                  cascade='all, delete-orphan',
                                  back_populates='trunk')

    outcalls = association_proxy('outcall_trunks', 'outcall',
                                 creator=lambda _outcall: OutcallTrunk(outcall=_outcall))

    register_iax = relationship('StaticIAX',
                                primaryjoin="""and_(
                                       TrunkFeatures.protocol == 'iax',
                                       TrunkFeatures.registerid == StaticIAX.id
                                )""",
                                foreign_keys='TrunkFeatures.registerid',
                                viewonly=True,
                                back_populates='trunk')

    register_sip = relationship('StaticSIP',
                                primaryjoin="""and_(
                                       TrunkFeatures.protocol == 'sip',
                                       TrunkFeatures.registerid == StaticSIP.id
                                )""",
                                foreign_keys='TrunkFeatures.registerid',
                                viewonly=True,
                                back_populates='trunk')

    @hybrid_property
    def endpoint(self):
        return self.protocol

    @endpoint.setter
    def endpoint(self, value):
        self.protocol = value

    @hybrid_property
    def endpoint_id(self):
        return self.protocolid

    @endpoint_id.setter
    def endpoint_id(self, value):
        self.protocolid = value

    def is_associated(self, protocol=None):
        if protocol:
            return self.protocol == protocol and self.protocolid is not None
        return self.protocol is not None and self.protocolid is not None

    def is_associated_with(self, endpoint):
        return endpoint.same_protocol(self.protocol, self.protocolid)

    def associate_endpoint(self, endpoint):
        self.protocol = endpoint.endpoint_protocol()
        self.protocolid = endpoint.id

    def remove_endpoint(self):
        self.protocol = None
        self.protocolid = None
