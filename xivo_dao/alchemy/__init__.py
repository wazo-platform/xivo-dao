# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.outcall import OutcallTrunk
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail
