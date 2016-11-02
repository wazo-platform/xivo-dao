# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

# explicitly import modules that are referenced in relationship to prevent
# "mapper initialization" errors
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.outcall import OutcallTrunk
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.ivr import IVR
