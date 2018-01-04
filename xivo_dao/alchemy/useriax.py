# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import six

from collections import Iterable

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.helpers import errors
from xivo_dao.helpers.asterisk import (
    convert_ast_true_to_int,
    convert_int_to_ast_true,
)
from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


EXCLUDE_OPTIONS = {
    'id',
    'commented',
    'options',
}
EXCLUDE_OPTIONS_CONFD = {
    'name',
    'type',
    'host',
    'context',
    'category',
    'protocol',
}
AST_TRUE_INTEGER_COLUMNS = {
    'trunk',
    'adsi',
    'jitterbuffer',
    'forcejitterbuffer',
    'sendani',
    'qualifysmoothing',
    'immediate',
    'keyrotate',
}


class UserIAX(Base):

    __tablename__ = 'useriax'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('useriax__idx__category', 'category'),
        Index('useriax__idx__mailbox', 'mailbox'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(40), nullable=False)
    type = Column(Enum('friend', 'peer', 'user',
                       name='useriax_type',
                       metadata=Base.metadata),
                  nullable=False)
    username = Column(String(80))
    secret = Column(String(80), nullable=False, server_default='')
    dbsecret = Column(String(255), nullable=False, server_default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(Enum('default', 'omit', 'billing', 'documentation',
                           name='useriax_amaflags',
                           metadata=Base.metadata),
                      server_default='default')
    mailbox = Column(String(80))
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    trunk = Column(Integer, nullable=False, server_default='0')
    auth = Column(Enum('plaintext', 'md5', 'rsa', 'plaintext,md5', 'plaintext,rsa', 'md5,rsa', 'plaintext,md5,rsa',
                       name='useriax_auth',
                       metadata=Base.metadata),
                  nullable=False, server_default='plaintext,md5')
    encryption = Column(Enum('no', 'yes', 'aes128',
                             name='useriax_encryption',
                             metadata=Base.metadata))
    forceencryption = Column(Enum('no', 'yes', 'aes128',
                                  name='useriax_encryption',
                                  metadata=Base.metadata))
    maxauthreq = Column(Integer)
    inkeys = Column(String(80))
    outkey = Column(String(80))
    adsi = Column(Integer)
    transfer = Column(Enum('no', 'yes', 'mediaonly',
                           name='useriax_transfer',
                           metadata=Base.metadata))
    codecpriority = Column(Enum('disabled', 'host', 'caller', 'reqonly',
                                name='useriax_codecpriority',
                                metadata=Base.metadata))
    jitterbuffer = Column(Integer)
    forcejitterbuffer = Column(Integer)
    sendani = Column(Integer, nullable=False, server_default='0')
    qualify = Column(String(4), nullable=False, server_default='no')
    qualifysmoothing = Column(Integer, nullable=False, server_default='0')
    qualifyfreqok = Column(Integer, nullable=False, server_default='60000')
    qualifyfreqnotok = Column(Integer, nullable=False, server_default='10000')
    timezone = Column(String(80))
    disallow = Column(String(100))
    allow = Column(Text)
    mohinterpret = Column(String(80))
    mohsuggest = Column(String(80))
    deny = Column(String(31))
    permit = Column(String(31))
    defaultip = Column(String(255))
    sourceaddress = Column(String(255))
    setvar = Column(String(100), nullable=False, server_default='')
    host = Column(String(255), nullable=False, server_default='dynamic')
    port = Column(Integer)
    mask = Column(String(15))
    regexten = Column(String(80))
    peercontext = Column(String(80))
    immediate = Column(Integer)
    keyrotate = Column(Integer)
    parkinglot = Column(Integer)
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='iax')
    category = Column(Enum('user', 'trunk',
                           name='useriax_category',
                           metadata=Base.metadata),
                      nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    requirecalltoken = Column(String(4), nullable=False, server_default='no')
    _options = Column("options", ARRAY(String, dimensions=2),
                      nullable=False, default=list, server_default='{}')

    trunk_rel = relationship('TrunkFeatures',
                             primaryjoin="""and_(
                                 TrunkFeatures.protocol == 'iax',
                                 TrunkFeatures.protocolid == UserIAX.id
                             )""",
                             foreign_keys='TrunkFeatures.protocolid',
                             uselist=False,
                             viewonly=True,
                             back_populates='endpoint_iax')

    @property
    def options(self):
        return self.all_options(EXCLUDE_OPTIONS_CONFD)

    def all_options(self, exclude=None):
        native_options = list(self.native_options(exclude))
        return native_options + self._options

    def native_options(self, exclude=None):
        for column in self.native_option_names(exclude):
            value = self.native_option(column)
            if value is not None:
                yield [column, value]

    def native_option(self, column_name):
        value = getattr(self, column_name, None)
        if value is not None and value != "":
            if column_name in AST_TRUE_INTEGER_COLUMNS:
                return convert_int_to_ast_true(value)
            else:
                return six.text_type(value)
        return None

    @options.setter
    def options(self, options):
        option_names = self.native_option_names(EXCLUDE_OPTIONS_CONFD)
        self.reset_options()
        self.set_options(option_names, options)

    def reset_options(self):
        self.reset_extra_options()
        self.reset_native_options()

    def reset_extra_options(self):
        self._options = []

    def reset_native_options(self):
        defaults = self.option_defaults()
        for column in self.native_option_names(EXCLUDE_OPTIONS_CONFD):
            value = defaults.get(column, None)
            setattr(self, column, value)

    def set_options(self, option_names, options):
        self.validate_options(options)
        for option in options:
            self.validate_option(option)
            column, value = option
            if column in option_names:
                self.set_native_option(column, value)
            else:
                self.add_extra_option(column, value)

    def validate_options(self, options):
        if not isinstance(options, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')

    def validate_option(self, option):
        if not isinstance(option, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')
        if not len(option) == 2:
            raise errors.wrong_type('options', 'list of pair of strings')
        for i in option:
            if not isinstance(i, (str, six.text_type)):
                raise errors.wrong_type('options', "value '{}' is not a string".format(i))

    def set_native_option(self, column, value):
        if column in AST_TRUE_INTEGER_COLUMNS:
            value = convert_ast_true_to_int(value)
        setattr(self, column, value)

    def add_extra_option(self, name, value):
        self._options.append([name, value])

    def native_option_names(self, exclude=None):
        exclude = set(exclude or []).union(EXCLUDE_OPTIONS)
        return set(column.name for column in self.__table__.columns) - exclude

    def option_defaults(self):
        defaults = {}
        for column in self.__table__.columns:
            if column.server_default:
                defaults[column.name] = column.server_default.arg
        return defaults

    def endpoint_protocol(self):
        return 'iax'

    def same_protocol(self, protocol, id):
        return protocol == 'iax' and self.id == id
