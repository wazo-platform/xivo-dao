# -*- coding: utf-8 -*-
# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.alchemy import enum
from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.asterisk import AsteriskOptionsMixin


class UserSIP(Base, AsteriskOptionsMixin):

    EXCLUDE_OPTIONS = {
        'id',
        'commented',
        'options',
        'tenant_uuid',
    }
    EXCLUDE_OPTIONS_CONFD = {
        'name',
        'username',
        'secret',
        'type',
        'host',
        'context',
        'category',
        'protocol'
    }
    AST_TRUE_INTEGER_COLUMNS = {
        'allowoverlap',
        'allowsubscribe',
        'allowtransfer',
        'autoframing',
        'buggymwi',
        'callcounter',
        'encryption',
        'g726nonstandard',
        'ignoresdpversion',
        'promiscredir',
        'rfc2833compensate',
        'snom_aoc_enabled',
        'subscribemwi',
        't38pt_udptl',
        't38pt_usertpsource',
        'textsupport',
        'trustrpid',
        'use_q850_reason',
        'useclientcode',
        'usereqphone',
    }

    __tablename__ = 'usersip'

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    name = Column(String(40), nullable=False)
    type = Column(Enum('friend', 'peer', 'user',
                       name='useriax_type',
                       metadata=Base.metadata),
                  nullable=False)
    username = Column(String(80))
    secret = Column(String(80), nullable=False, server_default='')
    md5secret = Column(String(32), nullable=False, server_default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(Enum('default', 'omit', 'billing', 'documentation',
                           name='useriax_amaflags',
                           metadata=Base.metadata),
                      nullable=False, server_default='default')
    allowtransfer = Column(Integer)
    fromuser = Column(String(80))
    fromdomain = Column(String(255))
    subscribemwi = Column(Integer, nullable=False, server_default='0')
    buggymwi = Column(Integer)
    call_limit = Column('call-limit', Integer, nullable=False, server_default='10')
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    maxcallbitrate = Column(Integer)
    insecure = Column(Enum('port', 'invite', 'port,invite',
                           name='usersip_insecure',
                           metadata=Base.metadata))
    nat = Column(Enum('no', 'force_rport', 'comedia', 'force_rport,comedia', 'auto_force_rport',
                      'auto_comedia', 'auto_force_rport,auto_comedia',
                      name='usersip_nat',
                      metadata=Base.metadata))
    promiscredir = Column(Integer)
    usereqphone = Column(Integer)
    videosupport = Column(Enum('no', 'yes', 'always',
                               name='usersip_videosupport',
                               metadata=Base.metadata))
    trustrpid = Column(Integer)
    sendrpid = Column(String(16))
    allowsubscribe = Column(Integer)
    allowoverlap = Column(Integer)
    dtmfmode = Column(Enum('rfc2833', 'inband', 'info', 'auto',
                           name='usersip_dtmfmode',
                           metadata=Base.metadata))
    rfc2833compensate = Column(Integer)
    qualify = Column(String(4))
    g726nonstandard = Column(Integer)
    disallow = Column(String(100))
    allow = Column(Text)
    autoframing = Column(Integer)
    mohinterpret = Column(String(80))
    useclientcode = Column(Integer)
    progressinband = Column(Enum('no', 'yes', 'never',
                                 name='usersip_progressinband',
                                 metadata=Base.metadata))
    t38pt_udptl = Column(Integer)
    t38pt_usertpsource = Column(Integer)
    rtptimeout = Column(Integer)
    rtpholdtimeout = Column(Integer)
    rtpkeepalive = Column(Integer)
    deny = Column(String(31))
    permit = Column(String(31))
    defaultip = Column(String(255))
    host = Column(String(255), nullable=False, server_default='dynamic')
    port = Column(Integer)
    regexten = Column(String(80))
    subscribecontext = Column(String(80))
    vmexten = Column(String(40))
    callingpres = Column(Integer)
    parkinglot = Column(Integer)
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='sip')
    category = Column(Enum('user', 'trunk',
                           name='useriax_category',
                           metadata=Base.metadata),
                      nullable=False)
    outboundproxy = Column(String(1024))
    transport = Column(String(255))
    remotesecret = Column(String(255))
    directmedia = Column(String(20))
    callcounter = Column(Integer)
    busylevel = Column(Integer)
    ignoresdpversion = Column(Integer)
    session_timers = Column('session-timers',
                            Enum('originate', 'accept', 'refuse',
                                 name='usersip_session_timers',
                                 metadata=Base.metadata))
    session_expires = Column('session-expires', Integer)
    session_minse = Column('session-minse', Integer)
    session_refresher = Column('session-refresher',
                               Enum('uac', 'uas',
                                    name='usersip_session_refresher',
                                    metadata=Base.metadata))
    callbackextension = Column(String(255))
    timert1 = Column(Integer)
    timerb = Column(Integer)
    qualifyfreq = Column(Integer)
    contactpermit = Column(String(1024))
    contactdeny = Column(String(1024))
    unsolicited_mailbox = Column(String(1024))
    use_q850_reason = Column(Integer)
    encryption = Column(Integer)
    snom_aoc_enabled = Column(Integer)
    maxforwards = Column(Integer)
    disallowed_methods = Column(String(1024))
    textsupport = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    _options = Column("options", ARRAY(String, dimensions=2),
                      nullable=False, default=list, server_default='{}')

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('usersip__idx__category', 'category'),
        CheckConstraint(
            directmedia.in_(
                ['no', 'yes', 'nonat', 'update', 'update,nonat', 'outgoing'])),
    )

    line = relationship('LineFeatures',
                        primaryjoin="""and_(
                            LineFeatures.protocol == 'sip',
                            LineFeatures.protocolid == UserSIP.id
                        )""",
                        foreign_keys='LineFeatures.protocolid',
                        uselist=False,
                        viewonly=True,
                        back_populates='endpoint_sip')

    trunk = relationship('TrunkFeatures',
                         primaryjoin="""and_(
                            TrunkFeatures.protocol == 'sip',
                            TrunkFeatures.protocolid == UserSIP.id
                         )""",
                         foreign_keys='TrunkFeatures.protocolid',
                         uselist=False,
                         viewonly=True,
                         back_populates='endpoint_sip')

    def same_protocol(self, protocol, id):
        return protocol == 'sip' and self.id == id

    def update_caller_id(self, user, extension=None):
        name, num = user.extrapolate_caller_id(extension)
        self.callerid = '"{}"'.format(name)
        if num:
            self.callerid += " <{}>".format(num)

    def clear_caller_id(self):
        self.callerid = None

    def endpoint_protocol(self):
        return 'sip'
