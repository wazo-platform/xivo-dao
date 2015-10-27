# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    Index
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.types import Integer, String, Text, Enum
from xivo_dao.alchemy import enum

from xivo_dao.helpers.exception import InputError

EXCLUDE_OPTIONS = {'id',
                   'name',
                   'username',
                   'secret',
                   'type',
                   'host',
                   'context',
                   'category',
                   'commented'}


class UserSIP(Base):

    __tablename__ = 'usersip'

    id = Column(Integer, nullable=False)
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
    nat = Column(Enum('no', 'force_rport', 'comedia', 'force_rport,comedia',
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
    setvar = Column(String(100), nullable=False, server_default='')
    host = Column(String(255), nullable=False, server_default='dynamic')
    port = Column(Integer)
    regexten = Column(String(80))
    subscribecontext = Column(String(80))
    fullcontact = Column(String(255))
    vmexten = Column(String(40))
    callingpres = Column(Integer)
    ipaddr = Column(String(255), nullable=False, server_default='')
    regseconds = Column(Integer, nullable=False, server_default='0')
    regserver = Column(String(20))
    lastms = Column(String(15), nullable=False, server_default='')
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
    registertrying = Column(Integer)
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

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('usersip__idx__category', 'category'),
        CheckConstraint(
            directmedia.in_(
                ['no', 'yes', 'nonat', 'update', 'update,nonat', 'outgoing'])),
    )

    @property
    def options(self):
        return list(self.map_options())

    def map_options(self):
        for column, attribute in self.option_names():
            for value in self.map_option(attribute):
                yield [column, value]

    def map_option(self, name):
        if name == 'subscribemwi':
            if self.subscribemwi == 1:
                yield 'yes'
            else:
                yield 'no'
        elif name == 'regseconds':
            if self.regseconds != 0:
                yield unicode(self.regseconds)
        elif name == 'allow':
            if self.allow is not None:
                allow = self.allow.split(",") if self.allow else []
                for value in allow:
                    yield value
        else:
            value = getattr(self, name, None)
            if value is not None and value != "":
                yield unicode(value)

    @options.setter
    def options(self, options):
        option_names = dict(self.option_names())
        self.reset_options(option_names)
        self.set_options(option_names, options)

    def reset_options(self, option_names):
        defaults = self.option_defaults()
        for column, attribute in option_names.iteritems():
            value = defaults.get(column, None)
            setattr(self, attribute, value)

    def set_options(self, option_names, options):
        for column, value in options:
            if column not in option_names:
                raise InputError("Unknown options parameter: {}".format(column))
            attribute = option_names[column]
            self.set_option(attribute, value)

    def set_option(self, attribute, value):
        if attribute == 'subscribemwi':
            self.subscribemwi = 1 if value == 'yes' else 0
        elif attribute == 'allow':
            allow = self.allow.split(',') if self.allow else []
            allow.append(value)
            self.allow = ",".join(allow)
        else:
            setattr(self, attribute, value)

    def option_names(self):
        for column in self.__table__.columns:
            if column.name not in EXCLUDE_OPTIONS:
                yield column.name, column.name.replace("-", "_")

    def option_defaults(self):
        defaults = {}
        for column in self.__table__.columns:
            if column.server_default:
                defaults[column.name] = column.server_default.arg
        return defaults
