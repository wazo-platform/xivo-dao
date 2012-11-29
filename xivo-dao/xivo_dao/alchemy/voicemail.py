# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.base import Base, Type
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text, Float, Enum


class Voicemail(Base):

    __tablename__ = 'voicemail'

    uniqueid = Column(Integer, primary_key=True, nullable=False)
    context = Column(String(39), nullable=False)
    mailbox = Column(String(40), nullable=False)
    password = Column(String(80), nullable=False, default='')
    fullname = Column(String(80), nullable=False, default='')
    email = Column(String(80))
    pager = Column(String(80))
    dialout = Column(String(39))
    callback = Column(String(39))
    exitcontext = Column(String(39))
    language = Column(String(20))
    tz = Column(String(80))
    attach = Column(Integer)
    saycid = Column(Integer)
    review = Column(Integer)
    operator = Column(Integer)
    envelope = Column(Integer)
    sayduration = Column(Integer)
    saydurationm = Column(Integer)
    sendvoicemail = Column(Integer)
    deletevoicemail = Column(Integer, nullable=False, default=0)
    sendvoicemail = Column(Integer)
    forcegreetings = Column(Integer)
    hidefromdir = Column(Enum('yes', 'no', name='voicemail_hidefromdir', metadata=Type.metadata),
                         nullable=False,
                         default='no')
    maxmsg = Column(Integer)
    emailsubject = Column(String(1024))
    emailbody = Column(Text)
    imapuser = Column(String(1024))
    imappassword = Column(String(1024))
    imapfolder = Column(String(1024))
    imapvmsharedid = Column(String(1024))
    attachfmt = Column(String(1024))
    serveremail = Column(String(1024))
    locale = Column(String(1024))
    tempgreetwarn = Column(Integer)
    messagewrap = Column(Integer)
    moveheard = Column(Integer)
    minsecs = Column(Integer)
    maxsecs = Column(Integer)
    nextaftercmd = Column(Integer)
    backupdeleted = Column(Integer)
    volgain = Column(Float)
    passwordlocation = Column(Enum('spooldir', 'voicemail', name='voicemail_passwordlocation', metadata=Type.metadata))
    commented = Column(Integer, nullable=False, default=0)
