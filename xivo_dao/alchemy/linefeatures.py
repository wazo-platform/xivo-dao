# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import re

from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Text
from sqlalchemy.schema import Column, UniqueConstraint, PrimaryKeyConstraint, \
    Index

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


caller_id_regex = re.compile(r'''
                             "                      #name start
                             (?P<name>[^"]+)        #inside ""
                             "                      #name end
                             \s+                    #space between name and number
                             (
                             <                      #number start
                             (?P<num>\+?[\dA-Z]+)   #inside <>
                             >                      #number end
                             )?                     #number is optional
                             ''', re.VERBOSE)


class LineFeatures(Base):

    CALLER_ID = '"{name}" <{num}>'

    __tablename__ = 'linefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        UniqueConstraint('protocol', 'protocolid'),
        Index('linefeatures__idx__context', 'context'),
        Index('linefeatures__idx__device', 'device'),
        Index('linefeatures__idx__number', 'number'),
        Index('linefeatures__idx__provisioningid', 'provisioningid'),
    )

    id = Column(Integer)
    protocol = Column(enum.trunk_protocol)
    protocolid = Column(Integer)
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128))
    number = Column(String(40))
    context = Column(String(39), nullable=False)
    provisioningid = Column(Integer, nullable=False, server_default='0')
    num = Column(Integer, server_default='1')
    ipfrom = Column(String(15))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    sip_endpoint = relationship("UserSIP",
                                primaryjoin="""and_(
                                    LineFeatures.protocol == 'sip',
                                    LineFeatures.protocolid == UserSIP.id
                                )""",
                                foreign_keys=[protocolid])

    sccp_endpoint = relationship("SCCPLine",
                                 primaryjoin="""and_(
                                 LineFeatures.protocol == 'sccp',
                                 LineFeatures.protocolid == SCCPLine.id
                                 )""",
                                 foreign_keys=[protocolid])

    @property
    def caller_id_name(self):
        if self.protocol == 'sccp':
            return self.sccp_endpoint.cid_name
        elif self.protocol == 'sip':
            return self._sip_caller_id_name()

    @caller_id_name.setter
    def caller_id_name(self, value):
        if self.protocol == 'sip':
            callerid = self.CALLER_ID.format(name=value,
                                             num=self._sip_caller_id_num())
            self.sip_endpoint.callerid = callerid
        elif self.protocol == 'sccp':
            self.sccp_endpoint.cid_name = value

    @property
    def caller_id_num(self):
        if self.protocol == 'sccp':
            return self.sccp_endpoint.cid_num
        elif self.protocol == 'sip':
            return self._sip_caller_id_num()

    @caller_id_num.setter
    def caller_id_num(self, value):
        if self.protocol == 'sip':
            callerid = self.CALLER_ID.format(name=self._sip_caller_id_name(),
                                             num=value)
            self.sip_endpoint.callerid = callerid
        elif self.protocol == 'sccp':
            self.sccp_endpoint.cid_num = value

    def _sip_caller_id_name(self):
        match = caller_id_regex.match(self.sip_endpoint.callerid)
        return match.group('name')

    def _sip_caller_id_num(self):
        match = caller_id_regex.match(self.sip_endpoint.callerid)
        return match.group('num')

    @property
    def endpoint(self):
        return self.protocol

    @endpoint.setter
    def endpoint(self, value):
        self.protocol = value

    @property
    def endpoint_id(self):
        return self.protocolid

    @endpoint_id.setter
    def endpoint_id(self, value):
        self.protocolid = value

    @property
    def provisioning_code(self):
        if self.provisioningid is None:
            return None
        if self.provisioningid == 0:
            return None
        return unicode(self.provisioningid)

    @provisioning_code.setter
    def provisioning_code(self, value):
        if value is None:
            self.provisioningid = 0
        elif value.isdigit():
            self.provisioningid = int(value)
        else:
            raise ValueError("provisioning_code '{}' are not digits".format(value))

    @property
    def position(self):
        return self.num

    @position.setter
    def position(self, value):
        self.num = value
