# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.helpers.asterisk import AsteriskOptionsMixin
from xivo_dao.helpers.db_manager import Base

from . import enum


class UserIAX(Base, AsteriskOptionsMixin):
    """
    Contains IAX Endpoints.
    https://wazo-platform.org/uc-doc/administration/interconnections/introduction
    """
    EXCLUDE_OPTIONS = {
        'id',
        'commented',
        'options',
        'tenant_uuid',
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

    __tablename__ = 'useriax'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('useriax__idx__category', 'category'),
        Index('useriax__idx__mailbox', 'mailbox'),
        Index('useriax__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(40), nullable=False)
    type = Column(
        Enum(
            'friend',
            'peer',
            'user',
            name='useriax_type',
            metadata=Base.metadata
        ),
        nullable=False,
    )
    username = Column(String(80))
    secret = Column(String(80), nullable=False, server_default='')
    dbsecret = Column(String(255), nullable=False, server_default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(
        Enum('default', 'omit', 'billing', 'documentation', name='useriax_amaflags', metadata=Base.metadata),
        server_default='default',
    )
    mailbox = Column(String(80))
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    trunk = Column(Integer, nullable=False, server_default='0')
    auth = Column(
        Enum(
            'plaintext', 'md5', 'rsa', 'plaintext,md5', 'plaintext,rsa', 'md5,rsa', 'plaintext,md5,rsa',
            name='useriax_auth',
            metadata=Base.metadata
        ),
        nullable=False,
        server_default='plaintext,md5'
    )
    encryption = Column(Enum('no', 'yes', 'aes128', name='useriax_encryption', metadata=Base.metadata))
    forceencryption = Column(Enum('no', 'yes', 'aes128', name='useriax_encryption', metadata=Base.metadata))
    maxauthreq = Column(Integer)
    inkeys = Column(String(80))
    outkey = Column(String(80))
    adsi = Column(Integer)
    transfer = Column(Enum('no', 'yes', 'mediaonly', name='useriax_transfer', metadata=Base.metadata))
    codecpriority = Column(
        Enum('disabled', 'host', 'caller', 'reqonly', name='useriax_codecpriority', metadata=Base.metadata)
    )
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
    category = Column(Enum('user', 'trunk', name='useriax_category', metadata=Base.metadata), nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    requirecalltoken = Column(String(4), nullable=False, server_default='no')
    _options = Column("options", ARRAY(String, dimensions=2), nullable=False, default=list, server_default='{}')

    trunk_rel = relationship('TrunkFeatures', uselist=False, viewonly=True)

    def endpoint_protocol(self):
        return 'iax'

    def same_protocol(self, protocol, id):
        return protocol == 'iax' and self.id == id
