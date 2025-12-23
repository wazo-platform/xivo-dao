# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from sqlalchemy import ForeignKeyConstraint, func, sql
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
    UniqueConstraint,
)
from sqlalchemy.sql.expression import bindparam, select
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.exception import InputError

from .context import Context
from .endpoint_sip import EndpointSIP
from .sccpline import SCCPLine

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
        Index('linefeatures__idx__endpoint_sccp_id', 'endpoint_sccp_id'),
        Index('linefeatures__idx__endpoint_custom_id', 'endpoint_custom_id'),
        Index('linefeatures__idx__application_uuid', 'application_uuid'),
        Index('linefeatures__idx__endpoint_sip_uuid', 'endpoint_sip_uuid'),
        ForeignKeyConstraint(
            ('context',),
            ('context.name',),
            ondelete='CASCADE',
        ),
    )

    id = Column(Integer)
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128))
    number = Column(String(40))
    context = Column(String(79), nullable=False)
    provisioningid = Column(Integer, nullable=False)
    num = Column(Integer, server_default='1')
    ipfrom = Column(String(15))
    application_uuid = Column(
        String(36), ForeignKey('application.uuid', ondelete='SET NULL')
    )
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    endpoint_sip_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('endpoint_sip.uuid', ondelete='SET NULL'),
    )
    endpoint_sccp_id = Column(Integer, ForeignKey('sccpline.id', ondelete='SET NULL'))
    endpoint_custom_id = Column(
        Integer, ForeignKey('usercustom.id', ondelete='SET NULL')
    )

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
        return sql.case(
            (cls.endpoint_sip_uuid.isnot(None), 'sip'),
            (cls.endpoint_sccp_id.isnot(None), 'sccp'),
            (cls.endpoint_custom_id.isnot(None), 'custom'),
            else_=None,
        )

    @hybrid_property
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

    @caller_id_name.expression
    def caller_id_name(cls):
        regex = '"([^"]+)"\\s+'

        return sql.case(
            (
                cls.endpoint_sip_uuid.isnot(None),
                cls._sip_query_option('callerid', 'endpoint', regex_filter=regex),
            ),
            (cls.endpoint_sccp_id.isnot(None), cls._sccp_query_option('cid_name')),
            else_=None,
        )

    @caller_id_name.setter
    def caller_id_name(self, value):
        if value is None:
            if (
                self.endpoint_sip_uuid
                or self.endpoint_sccp_id
                or self.endpoint_custom_id
            ):
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

    @hybrid_property
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

    @caller_id_num.expression
    def caller_id_num(cls):
        regex = '<([0-9A-Z]+)?>'

        return sql.case(
            (
                cls.endpoint_sip_uuid.isnot(None),
                cls._sip_query_option('callerid', 'endpoint', regex_filter=regex),
            ),
            (cls.endpoint_sccp_id.isnot(None), cls._sccp_query_option('cid_num')),
        )

    @caller_id_num.setter
    def caller_id_num(self, value):
        if value is None:
            if (
                self.endpoint_sip_uuid
                or self.endpoint_sccp_id
                or self.endpoint_custom_id
            ):
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
        return str(self.provisioningid)

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
        return (
            sql.select(Context.tenant_uuid)
            .where(
                Context.name == cls.context,
            )
            .label('tenant_uuid')
        )

    @hybrid_property
    def registrar(self):
        return self.configregistrar

    @registrar.setter
    def registrar(self, value):
        self.configregistrar = value

    def is_associated(self):
        return (
            self.endpoint_sip_uuid or self.endpoint_sccp_id or self.endpoint_custom_id
        )

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

    @classmethod
    def _sip_query_option(cls, option, section=None, regex_filter=None):
        attr = EndpointSIP._get_sip_option_expression(option, section)
        if regex_filter:
            attr = func.unnest(
                func.regexp_matches(
                    attr, bindparam('regexp', regex_filter, unique=True)
                )
            )

        return (
            select(attr)
            .where(EndpointSIP.uuid == cls.endpoint_sip_uuid)
            .scalar_subquery()
        )

    @classmethod
    def _sccp_query_option(cls, option):
        if option not in dir(SCCPLine):
            return

        return (
            select(getattr(SCCPLine, option))
            .where(SCCPLine.id == cls.endpoint_sccp_id)
            .scalar_subquery()
        )
