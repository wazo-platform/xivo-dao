# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text


class UserSIP(Base):

    __tablename__ = 'usersip'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    type = Column(String(8), nullable=False)
    username = Column(String(80))
    secret = Column(String(80), nullable=False, default='')
    md5secret = Column(String(32), nullable=False, default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(String(16), nullable=False, default='default')
    allowtransfer = Column(Integer)
    fromuser = Column(String(80))
    fromdomain = Column(String(255))
    mailbox = Column(String(80))
    subscribemwi = Column(Integer, nullable=False, default=0)
    buggymwi = Column(Integer)
    call_limit = Column('call-limit', Integer, nullable=False, default=0)
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    maxcallbitrate = Column(Integer)
    insecure = Column(String(16))
    nat = Column(String(16))
    promiscredir = Column(Integer)
    usereqphone = Column(Integer)
    videosupport = Column(String(16))
    trustrpid = Column(Integer)
    sendrpid = Column(Integer)
    allowsubscribe = Column(Integer)
    allowoverlap = Column(Integer)
    dtmfmode = Column(String(16))
    rfc2833compensate = Column(Integer)
    qualify = Column(String(4))
    g726nonstandard = Column(Integer)
    disallow = Column(String(100))
    allow = Column(Text)
    autoframing = Column(Integer)
    mohinterpret = Column(String(80))
    mohsuggest = Column(String(80))
    useclientcode = Column(Integer)
    progressinband = Column(String(16))
    t38pt_udptl = Column(Integer)
    t38pt_usertpsource = Column(Integer)
    rtptimeout = Column(Integer)
    rtpholdtimeout = Column(Integer)
    rtpkeepalive = Column(Integer)
    deny = Column(String(31))
    permit = Column(String(31))
    defaultip = Column(String(255))
    setvar = Column(String(100), nullable=False, default='')
    host = Column(String(255), nullable=False, default='dynamic')
    port = Column(Integer)
    regexten = Column(String(80))
    subscribecontext = Column(String(80))
    fullcontact = Column(String(255))
    vmexten = Column(String(40))
    callingpres = Column(Integer)
    ipaddr = Column(String(255), nullable=False, default='')
    regseconds = Column(Integer, nullable=False, default=0)
    regserver = Column(String(20))
    lastms = Column(String(15), nullable=False, default='')
    parkinglot = Column(Integer)
    protocol = Column(String(8), nullable=False, default='sip')
    category = Column(String(8))
    outboundproxy = Column(String(1024))
    transport = Column(String(255))
    remotesecret = Column(String(255))
    directmedia = Column(String(16))
    callcounter = Column(Integer)
    busylevel = Column(Integer)
    ignoresdpversion = Column(Integer)
    session_timers = Column('session-timers', String(16))
    session_expires = Column('session-expires', Integer)
    session_minse = Column('session-minse', Integer)
    session_refresher = Column('session-refresher', String(16))
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
    commented = Column(Integer, nullable=False, default=0)
