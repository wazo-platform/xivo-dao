# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
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

from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text


class UserFeatures(Base):
    __tablename__ = 'userfeatures'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(128), nullable=False, server_default='')
    lastname = Column(String(128), nullable=False, server_default='')
    voicemailtype = Column(String(128))  # Should be Enum
    voicemailid = Column(Integer)
    agentid = Column(Integer)
    pictureid = Column(Integer)
    entityid = Column(Integer)
    callerid = Column(String(160))
    ringseconds = Column(Integer, nullable=False, default=30)
    simultcalls = Column(Integer, nullable=False, default=5)
    enableclient = Column(Integer, nullable=False, default=1)
    loginclient = Column(String(64), nullable=False, server_default='')
    passwdclient = Column(String(64), nullable=False, server_default='')
    profileclient = Column(String(64), nullable=False, server_default='')
    enablehint = Column(Integer, nullable=False, default=1)
    enablevoicemail = Column(Integer, nullable=False, default=0)
    enablexfer = Column(Integer, nullable=False, default=0)
    enableautomon = Column(Integer, nullable=False, default=0)
    callrecord = Column(Integer, nullable=False, default=0)
    incallfilter = Column(Integer, nullable=False, default=0)
    enablednd = Column(Integer, nullable=False, default=0)
    enableunc = Column(Integer, nullable=False, default=0)
    destunc = Column(String(128), nullable=False, server_default='')
    enablerna = Column(Integer, nullable=False, default=0)
    destrna = Column(String(128), nullable=False, server_default='')
    enablebusy = Column(Integer, nullable=False, default=0)
    destbusy = Column(String(128), nullable=False, server_default='')
    musiconhold = Column(String(128), nullable=False, server_default='')
    outcallerid = Column(String(80), nullable=False, server_default='')
    mobilephonenumber = Column(String(128), nullable=False, server_default='')
    userfield = Column(String(128), nullable=False, server_default='')
    bsfilter = Column(String(128), nullable=False, server_default='no')  # Should be Enum
    preprocess_subroutine = Column(String(39))
    timezone = Column(String(128))
    language = Column(String(20))
    ringintern = Column(String(64))
    ringextern = Column(String(64))
    ringgroup = Column(String(64))
    ringforward = Column(String(64))
    rightcallcode = Column(String(16))
    alarmclock = Column(String(5), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, default=0)
    description = Column(Text)

    @property
    def fullname(self):
        return ' '.join([self.firstname, self.lastname])
