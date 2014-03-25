# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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


class MeetmeFeatures(Base):

    __tablename__ = 'meetmefeatures'

    id = Column(Integer, primary_key=True)
    meetmeid = Column(Integer, nullable=False)
    name = Column(String(80), nullable=False)
    confno = Column(String(40), nullable=False)
    context = Column(String(39), nullable=False, server_default='')
    admin_typefrom = Column(String(40))  # Should be Enum ('none', 'internal', 'external', 'undefined')
    admin_internalid = Column(Integer)
    admin_externalid = Column(String(40))
    admin_identification = Column(String(40))  # Should be Enum ('calleridnum', 'pin', 'all')
    admin_mode = Column(String(40))  # Should be Enum ('listen', 'talk', 'all')
    admin_announceusercount = Column(Integer, nullable=False, server_default='0')
    admin_announcejoinleave = Column(String(40))  # Should be Enum ('no', 'yes', 'noreview')
    admin_moderationmode = Column(Integer, nullable=False, server_default='0')
    admin_initiallymuted = Column(Integer, nullable=False, server_default='0')
    admin_musiconhold = Column(String(128))
    admin_poundexit = Column(Integer, nullable=False, server_default='0')
    admin_quiet = Column(Integer, nullable=False, server_default='0')
    admin_starmenu = Column(Integer, nullable=False, server_default='0')
    admin_closeconflastmarkedexit = Column(Integer, nullable=False, server_default='0')
    admin_enableexitcontext = Column(Integer, nullable=False, server_default='0')
    admin_exitcontext = Column(String(39))
    user_mode = Column(String(40))  # Should be Enum ('listen', 'talk', 'all')
    user_announceusercount = Column(Integer, nullable=False, server_default='0')
    user_hiddencalls = Column(Integer, nullable=False, server_default='0')
    user_announcejoinleave = Column(String(40))  # Should be Enum ('no', 'yes', 'noreview')
    user_initiallymuted = Column(Integer, nullable=False, server_default='0')
    user_musiconhold = Column(String(128))
    user_poundexit = Column(Integer, nullable=False, server_default='0')
    user_quiet = Column(Integer, nullable=False, server_default='0')
    user_starmenu = Column(Integer, nullable=False, server_default='0')
    user_enableexitcontext = Column(Integer, nullable=False, server_default='0')
    user_exitcontext = Column(String(39))
    talkeroptimization = Column(Integer, nullable=False, server_default='0')
    record = Column(Integer, nullable=False, server_default='0')
    talkerdetection = Column(Integer, nullable=False, server_default='0')
    noplaymsgfirstenter = Column(Integer, nullable=False, server_default='0')
    durationm = Column(Integer)
    closeconfdurationexceeded = Column(Integer, nullable=False, server_default='0')
    nbuserstartdeductduration = Column(Integer)
    timeannounceclose = Column(Integer)
    maxusers = Column(Integer, nullable=False, server_default='0')
    startdate = Column(Integer)
    emailfrom = Column(String(255))
    emailfromname = Column(String(255))
    emailsubject = Column(String(255))
    emailbody = Column(Text)
    preprocess_subroutine = Column(String(39))
    description = Column(Text)
    commented = Column(Integer, server_default='0')
