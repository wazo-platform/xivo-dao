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

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usersip import UserSIP


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
    provisioningid = Column(Integer, nullable=False)
    num = Column(Integer, server_default='1')
    ipfrom = Column(String(15))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    sip_endpoint = relationship(UserSIP,
                                primaryjoin="""and_(
                                    LineFeatures.protocol == 'sip',
                                    LineFeatures.protocolid == UserSIP.id
                                )""",
                                foreign_keys=[protocolid])

    sccp_endpoint = relationship(SCCPLine,
                                 primaryjoin="""and_(
                                 LineFeatures.protocol == 'sccp',
                                 LineFeatures.protocolid == SCCPLine.id
                                 )""",
                                 foreign_keys=[protocolid])

    @property
    def caller_id_name(self):
        if self.protocol == 'sip':
            return self._sip_caller_id_name()
        elif self.protocol == 'sccp':
            return self._sccp_caller_id_name()

    def _sip_caller_id_name(self):
        if self.sip_endpoint is None:
            return None

        if self.sip_endpoint.callerid is None:
            return None

        match = caller_id_regex.match(self.sip_endpoint.callerid)
        if not match:
            return None

        return match.group('name')

    def _sccp_caller_id_name(self):
        if self.sccp_endpoint is None:
            return None

        return self.sccp_endpoint.cid_name

    @caller_id_name.setter
    def caller_id_name(self, value):
        if value is None:
            raise InputError("cannot set caller name to None")
        if self.protocol == 'sip':
            self._set_sip_caller_id_name(value)
        elif self.protocol == 'sccp':
            self._set_sccp_caller_id_name(value)
        else:
            raise InputError("Line is not associated to an endpoint")

    def _set_sip_caller_id_name(self, value):
        num = self._sip_caller_id_num()
        callerid = self.CALLER_ID.format(name=value, num=num)
        self.sip_endpoint.callerid = callerid

    def _set_sccp_caller_id_name(self, value):
        self.sccp_endpoint.cid_name = value

    @property
    def caller_id_num(self):
        if self.protocol == 'sip':
            return self._sip_caller_id_num()
        elif self.protocol == 'sccp':
            return self._sccp_caller_id_num()

    def _sip_caller_id_num(self):
        if self.sip_endpoint is None:
            return None

        if self.sip_endpoint.callerid is None:
            return None

        match = caller_id_regex.match(self.sip_endpoint.callerid)
        if not match:
            return None

        return match.group('num')

    def _sccp_caller_id_num(self):
        if self.sccp_endpoint is None:
            return None

        return self.sccp_endpoint.cid_num

    @caller_id_num.setter
    def caller_id_num(self, value):
        if value is None:
            raise InputError("Cannot set caller num to None")
        if self.protocol == 'sip':
            self._set_sip_caller_id_num(value)
        elif self.protocol == 'sccp':
            self._set_sccp_caller_id_num(value)
        else:
            raise InputError("Line is not associated to an endpoint")

    def _set_sip_caller_id_num(self, value):
        name = self._sip_caller_id_name()
        callerid = self.CALLER_ID.format(name=name, num=value)
        self.sip_endpoint.callerid = callerid

    def _set_sccp_caller_id_num(self, value):
        self.sccp_endpoint.cid_num = value

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
    def provisioning_extension(self):
        return self.provisioning_code

    @property
    def provisioning_code(self):
        if self.provisioningid is None:
            return None
        return unicode(self.provisioningid)

    @provisioning_code.setter
    def provisioning_code(self, value):
        if value is None:
            self.provisioningid = None
        elif value.isdigit():
            self.provisioningid = int(value)

    @property
    def position(self):
        return self.num

    @position.setter
    def position(self, value):
        self.num = value

    @property
    def device_slot(self):
        return self.num

    @property
    def device_id(self):
        if self.device == '':
            return None
        return self.device

    @device_id.setter
    def device_id(self, value):
        value = value or ''
        self.device = value
