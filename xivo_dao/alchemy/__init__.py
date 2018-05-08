# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

# explicitly import modules that are referenced in relationship to prevent
# "mapper initialization" errors
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.asterisk_file_section import AsteriskFileSection
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.call_log_participant import CallLogParticipant
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.outcall import OutcallTrunk
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail

__all__ = [
    'AgentFeatures',
    'AsteriskFileSection',
    'AsteriskFileVariable',
    'CallLog',
    'CallLogParticipant',
    'Callfilter',
    'Callfiltermember',
    'Conference',
    'CtiProfile',
    'Dialaction',
    'Extension',
    'FuncKeyDestGroup',
    'FuncKeyDestPaging',
    'GroupFeatures',
    'IVR',
    'IVRChoice',
    'Incall',
    'LineExtension',
    'LineFeatures',
    'Outcall',
    'OutcallTrunk',
    'Paging',
    'PagingUser',
    'ParkingLot',
    'PickupMember',
    'QueueMember',
    'RightCall',
    'RightCallMember',
    'SCCPLine',
    'Schedule',
    'SchedulePath',
    'ScheduleTime',
    'StaticIAX',
    'StaticSIP',
    'Switchboard',
    'SwitchboardMemberUser',
    'Tenant',
    'TrunkFeatures',
    'UserCustom',
    'UserFeatures',
    'UserIAX',
    'UserLine',
    'UserSIP',
    'Voicemail',
]
