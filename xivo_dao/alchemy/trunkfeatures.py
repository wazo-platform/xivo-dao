# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, Index
from sqlalchemy.types import Integer, Text, String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
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

    endpoint_sip = relationship(UserSIP,
                                primaryjoin="""and_(
                                    TrunkFeatures.protocol == 'sip',
                                    TrunkFeatures.protocolid == UserSIP.id
                                )""",
                                foreign_keys=[protocolid],
                                backref=backref('trunk', uselist=False))

    endpoint_iax = relationship(UserIAX,
                                primaryjoin="""and_(
                                    TrunkFeatures.protocol == 'iax',
                                    TrunkFeatures.protocolid == UserIAX.id
                                )""",
                                foreign_keys=[protocolid],
                                backref=backref('trunk_rel', uselist=False))

    endpoint_custom = relationship(UserCustom,
                                   primaryjoin="""and_(
                                       TrunkFeatures.protocol == 'custom',
                                       TrunkFeatures.protocolid == UserCustom.id
                                   )""",
                                   foreign_keys=[protocolid],
                                   backref=backref('trunk', uselist=False))

    outcall_trunks = relationship('OutcallTrunk',
                                  cascade='all, delete-orphan',
                                  back_populates='trunk')

    outcalls = association_proxy('outcall_trunks', 'outcall',
                                 creator=lambda _outcall: OutcallTrunk(outcall=_outcall))

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
