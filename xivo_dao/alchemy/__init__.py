# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

# explicitly import modules that are referenced in relationship to prevent
# "mapper initialization" errors

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.application import Application
from xivo_dao.alchemy.application_dest_node import ApplicationDestNode
from xivo_dao.alchemy.asterisk_file_section import AsteriskFileSection
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.endpoint_sip import EndpointSIP, EndpointSIPTemplate
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition
from xivo_dao.alchemy.func_key_dest_parking import FuncKeyDestParking
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.ingress_http import IngressHTTP
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meeting import Meeting, MeetingOwner
from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.alchemy.moh import MOH
from xivo_dao.alchemy.outcall import Outcall, OutcallTrunk
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.alchemy.pjsip_transport_option import PJSIPTransportOption
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.voicemail import Voicemail

__all__ = [
    'AgentFeatures',
    'AgentQueueSkill',
    'Application',
    'ApplicationDestNode',
    'AsteriskFileSection',
    'AsteriskFileVariable',
    'Callfilter',
    'Callfiltermember',
    'Conference',
    'Context',
    'ContextInclude',
    'Dialaction',
    'EndpointSIP',
    'EndpointSIPTemplate',
    'EndpointSIPSection',
    'EndpointSIPSectionOption',
    'Extension',
    'FuncKeyDestAgent',
    'FuncKeyDestBSFilter',
    'FuncKeyDestConference',
    'FuncKeyDestGroup',
    'FuncKeyDestGroupMember',
    'FuncKeyDestPaging',
    'FuncKeyDestParkPosition',
    'FuncKeyDestParking',
    'FuncKeyDestQueue',
    'FuncKeyDestUser',
    'FuncKeyMapping',
    'GroupFeatures',
    'IngressHTTP',
    'IVR',
    'IVRChoice',
    'Incall',
    'LineExtension',
    'LineFeatures',
    'Meeting',
    'MeetingAuthorization',
    'MeetingOwner',
    'MOH',
    'Outcall',
    'OutcallTrunk',
    'Paging',
    'PagingUser',
    'ParkingLot',
    'PhoneNumber',
    'Pickup',
    'PickupMember',
    'PJSIPTransport',
    'PJSIPTransportOption',
    'QueueMember',
    'QueueSkill',
    'RightCall',
    'RightCallMember',
    'SCCPLine',
    'Schedule',
    'SchedulePath',
    'ScheduleTime',
    'StaticIAX',
    'Switchboard',
    'SwitchboardMemberUser',
    'Tenant',
    'TrunkFeatures',
    'UserCustom',
    'UserFeatures',
    'UserIAX',
    'UserLine',
    'Voicemail',
]
