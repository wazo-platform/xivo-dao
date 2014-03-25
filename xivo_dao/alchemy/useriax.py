# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class UserIAX(Base):

    __tablename__ = 'useriax'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    type = Column(String(8), nullable=False)
    username = Column(String(80))
    secret = Column(String(80), nullable=False, server_default='')
    dbsecret = Column(String(255), nullable=False, server_default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(String(16), nullable=False, server_default='default')
    mailbox = Column(String(80))
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    trunk = Column(Integer, nullable=False, server_default='0')
    auth = Column(String(16), nullable=False, server_default='plaintext,md5')
    encryption = Column(String(8))
    forceencryption = Column(String(8))
    maxauthreq = Column(Integer)
    inkeys = Column(String(80))
    outkey = Column(String(80))
    adsi = Column(Integer)
    transfer = Column(String(16))
    codecpriority = Column(String(16))
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
    ipaddr = Column(String(255), nullable=False, server_default='')
    regseconds = Column(Integer, nullable=False, server_default='0')
    immediate = Column(Integer)
    keyrotate = Column(Integer)
    parkinglot = Column(Integer)
    protocol = Column(String(8), nullable=False, server_default='iax')
    category = Column(String(8))
    commented = Column(Integer, nullable=False, server_default='0')
    requirecalltoken = Column(String(4), nullable=False, server_default='no')
