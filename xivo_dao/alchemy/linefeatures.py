# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import re
import six

from sqlalchemy import sql
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Integer,
    String,
    Text,
)
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    Index,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.db_manager import Base
from .context import Context


caller_id_regex = re.compile(
    r'''
    "                      #name start
    (?P<name>[^"]+)        #inside ""
    "                      #name end
    \s+                    #space between name and number
    (
    <                      #number start
    (?P<num>\+?[\dA-Z]+)   #inside <>
    >                      #number end
    )?                     #number is optional
    ''',
    re.VERBOSE,
)


class LineFeatures(Base):

    CALLER_ID = '"{name}" <{num}>'

    __tablename__ = 'linefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        CheckConstraint(
            '''
            ( CASE WHEN endpoint_sip_uuid IS NULL THEN 0 ELSE 1 END
            + CASE WHEN endpoint_sccp_id IS NULL THEN 0 ELSE 1 END
            + CASE WHEN endpoint_custom_id IS NULL THEN 0 ELSE 1 END
            ) <= 1
            ''',
            name='linefeatures_endpoints_check',
        ),
        Index('linefeatures__idx__context', 'context'),
        Index('linefeatures__idx__device', 'device'),
        Index('linefeatures__idx__number', 'number'),
        Index('linefeatures__idx__provisioningid', 'provisioningid'),
    )

    id = Column(Integer)
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128))
    number = Column(String(40))
    context = Column(String(39), nullable=False)
    provisioningid = Column(Integer, nullable=False)
    num = Column(Integer, server_default='1')
    ipfrom = Column(String(15))
    application_uuid = Column(String(36), ForeignKey('application.uuid', ondelete='SET NULL'))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    endpoint_sip_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='SET NULL'),
    )
    endpoint_sccp_id = Column(Integer, ForeignKey('sccpline.id', ondelete='SET NULL'))
    endpoint_custom_id = Column(Integer, ForeignKey('usercustom.id', ondelete='SET NULL'))

    context_rel = relationship(
        'Context',
        primaryjoin='LineFeatures.context == Context.name',
        foreign_keys='LineFeatures.context',
        viewonly=True,
    )

    application = relationship('Application', viewonly=True)

    endpoint_sip = relationship('EndpointSIP', viewonly=True)
    endpoint_sccp = relationship('SCCPLine', viewonly=True)
    endpoint_custom = relationship('UserCustom', viewonly=True)

    line_extensions = relationship(
        'LineExtension',
        order_by='desc(LineExtension.main_extension)',
        cascade='all, delete-orphan',
        back_populates='line',
    )

    extensions = association_proxy('line_extensions', 'extension')

    user_lines = relationship(
        'UserLine',
        order_by='desc(UserLine.main_user)',
        cascade='all, delete-orphan',
        back_populates='line',
    )

    users = association_proxy('user_lines', 'user')

    @hybrid_property
    def protocol(self):
        if self.endpoint_sip_uuid:
            return 'sip'
        elif self.endpoint_sccp_id:
            return 'sccp'
        elif self.endpoint_custom_id:
            return 'custom'

    @protocol.expression
    def protocol(cls):
        return sql.case([
            (cls.endpoint_sip_uuid != None, 'sip'),
            (cls.endpoint_sccp_id != None, 'sccp'),
            (cls.endpoint_custom_id != None, 'custom'),
        ], else_=None)

    @property
    def caller_id_name(self):
        if self.endpoint_sip:
            return self._sip_caller_id_name()
        elif self.endpoint_sccp:
            return self._sccp_caller_id_name()

    def _sip_caller_id_name(self):
        if not self.endpoint_sip:
            return None

        for key, value in self.endpoint_sip.endpoint_section_options:
            if key != 'callerid':
                continue

            match = caller_id_regex.match(value)
            if not match:
                return None

            return match.group('name')

    def _sccp_caller_id_name(self):
        return self.endpoint_sccp.cid_name

    @caller_id_name.setter
    def caller_id_name(self, value):
        if value is None:
            if self.endpoint_sip_uuid or self.endpoint_sccp_id or self.endpoint_custom_id:
                raise InputError("Cannot set caller id to None")
            return

        if self.endpoint_sip_uuid:
            self._set_sip_caller_id_name(value)
        elif self.endpoint_sccp_id:
            self._set_sccp_caller_id_name(value)
        elif self.endpoint_custom_id:
            raise InputError("Cannot set caller id on endpoint of type 'custom'")
        else:
            raise InputError("Cannot set caller id if no endpoint associated")

    def _set_sip_caller_id_name(self, value):
        num = self._sip_caller_id_num()
        callerid = self.CALLER_ID.format(name=value, num=num)
        self.endpoint_sip.caller_id = callerid

    def _set_sccp_caller_id_name(self, value):
        self.endpoint_sccp.cid_name = value

    @property
    def caller_id_num(self):
        if self.endpoint_sip:
            return self._sip_caller_id_num()
        elif self.endpoint_sccp:
            return self._sccp_caller_id_num()

    def _sip_caller_id_num(self):
        if not self.endpoint_sip_uuid:
            return None

        for key, option in self.endpoint_sip.endpoint_section_options:
            if key != 'callerid':
                continue

            match = caller_id_regex.match(option)
            if not match:
                return None

            return match.group('num')

    def _sccp_caller_id_num(self):
        return self.endpoint_sccp.cid_num

    @caller_id_num.setter
    def caller_id_num(self, value):
        if value is None:
            if self.endpoint_sip_uuid or self.endpoint_sccp_id or self.endpoint_custom_id:
                raise InputError("Cannot set caller id num to None")
            return

        if self.endpoint_sip_uuid:
            self._set_sip_caller_id_num(value)
        elif self.endpoint_sccp_id:
            raise InputError("Cannot set caller id num on endpoint of type 'sccp'")
        elif self.endpoint_custom_id:
            raise InputError("Cannot set caller id on endpoint of type 'custom'")
        else:
            raise InputError("Cannot set caller id if no endpoint associated")

    def _set_sip_caller_id_num(self, value):
        name = self._sip_caller_id_name()
        callerid = self.CALLER_ID.format(name=name, num=value)
        self.endpoint_sip.caller_id = callerid

    @hybrid_property
    def provisioning_extension(self):
        return self.provisioning_code

    @hybrid_property
    def provisioning_code(self):
        if self.provisioningid is None:
            return None
        return six.text_type(self.provisioningid)

    @provisioning_code.expression
    def provisioning_code(cls):
        return sql.cast(sql.func.nullif(cls.provisioningid, 0), String)

    @provisioning_code.setter
    def provisioning_code(self, value):
        if value is None:
            self.provisioningid = None
        elif value.isdigit():
            self.provisioningid = int(value)

    @hybrid_property
    def position(self):
        return self.num

    @position.setter
    def position(self, value):
        self.num = value

    @hybrid_property
    def device_slot(self):
        return self.num

    @hybrid_property
    def device_id(self):
        if self.device == '':
            return None
        return self.device

    @device_id.expression
    def device_id(cls):
        return sql.func.nullif(cls.device, '')

    @device_id.setter
    def device_id(self, value):
        value = value or ''
        self.device = value

    @hybrid_property
    def tenant_uuid(self):
        return self.context_rel.tenant_uuid

    @tenant_uuid.expression
    def tenant_uuid(cls):
        return sql.select([Context.tenant_uuid]).where(
            Context.name == cls.context,
        ).label('tenant_uuid')

    @hybrid_property
    def registrar(self):
        return self.configregistrar

    @registrar.setter
    def registrar(self, value):
        self.configregistrar = value

    def is_associated(self):
        return self.endpoint_sip_uuid or self.endpoint_sccp_id or self.endpoint_custom_id

    def update_extension(self, extension):
        self.number = extension.exten
        self.context = extension.context

    def clear_extension(self):
        self.number = None

    def update_name(self):
        if self.endpoint_sip and self.endpoint_sip.name not in ("", None):
            self.name = self.endpoint_sip.name
        elif self.endpoint_sccp and self.endpoint_sccp.name not in ("", None):
            self.name = self.endpoint_sccp.name
        elif self.endpoint_custom and self.endpoint_custom.interface not in ("", None):
            self.name = self.endpoint_custom.interface
        else:
            self.name = None

    def associate_device(self, device):
        self.device = device.id

    def remove_device(self):
        self.device = ''
