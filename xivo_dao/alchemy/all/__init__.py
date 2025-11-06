# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agentglobalparams import AgentGlobalParams
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.application import Application
from xivo_dao.alchemy.application_dest_node import ApplicationDestNode
from xivo_dao.alchemy.asterisk_file import AsteriskFile
from xivo_dao.alchemy.asterisk_file_section import AsteriskFileSection
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.alchemy.blocklist import Blocklist
from xivo_dao.alchemy.blocklist_number import BlocklistNumber
from xivo_dao.alchemy.blocklist_user import BlocklistUser
from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.cel import CEL
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.contexttype import ContextType
from xivo_dao.alchemy.dhcp import Dhcp
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.endpoint_sip import EndpointSIP, EndpointSIPTemplate
from xivo_dao.alchemy.endpoint_sip_options_view import EndpointSIPOptionsView
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.external_app import ExternalApp
from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_features import FuncKeyDestFeatures
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition
from xivo_dao.alchemy.func_key_dest_parking import FuncKeyDestParking
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_type import FuncKeyType
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.infos import Infos
from xivo_dao.alchemy.ingress_http import IngressHTTP
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.mail import Mail
from xivo_dao.alchemy.meeting import Meeting, MeetingOwner
from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.alchemy.moh import MOH
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.alchemy.pjsip_transport_option import PJSIPTransportOption
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.resolvconf import Resolvconf
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallexten import RightCallExten
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.session import Session
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from xivo_dao.alchemy.stat_switchboard_queue import StatSwitchboardQueue
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.stats_conf import StatsConf
from xivo_dao.alchemy.stats_conf_agent import StatsConfAgent
from xivo_dao.alchemy.stats_conf_queue import StatsConfQueue
from xivo_dao.alchemy.stats_conf_xivouser import StatsConfXivoUser
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_external_app import UserExternalApp
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.voicemail import Voicemail

__all__ = [
    "AccessFeatures",
    "AgentLoginStatus",
    "AgentMembershipStatus",
    "AgentFeatures",
    "AgentGlobalParams",
    "AgentQueueSkill",
    "Application",
    "ApplicationDestNode",
    "AsteriskFile",
    "AsteriskFileSection",
    "AsteriskFileVariable",
    "Blocklist",
    "BlocklistNumber",
    "BlocklistUser",
    "Callerid",
    "Callfilter",
    "Callfiltermember",
    "CEL",
    "Conference",
    "Context",
    "ContextInclude",
    "ContextMember",
    "ContextNumbers",
    "ContextType",
    "Dhcp",
    "Dialaction",
    "DialPattern",
    "EndpointSIP",
    "EndpointSIPSection",
    "EndpointSIPSectionOption",
    "EndpointSIPOptionsView",
    "EndpointSIPTemplate",
    "Extension",
    "ExternalApp",
    "Features",
    "FeatureExtension",
    "FuncKey",
    "FuncKeyDestAgent",
    "FuncKeyDestBSFilter",
    "FuncKeyDestConference",
    "FuncKeyDestCustom",
    "FuncKeyDestFeatures",
    "FuncKeyDestForward",
    "FuncKeyDestGroup",
    "FuncKeyDestGroupMember",
    "FuncKeyDestPaging",
    "FuncKeyDestParkPosition",
    "FuncKeyDestParking",
    "FuncKeyDestQueue",
    "FuncKeyDestService",
    "FuncKeyDestUser",
    "FuncKeyDestinationType",
    "FuncKeyMapping",
    "FuncKeyTemplate",
    "FuncKeyType",
    "GroupFeatures",
    "IAXCallNumberLimits",
    "Incall",
    "Infos",
    "IngressHTTP",
    "IVR",
    "IVRChoice",
    "LineExtension",
    "LineFeatures",
    "Mail",
    "Meeting",
    "MeetingAuthorization",
    "MeetingOwner",
    "MOH",
    "Netiface",
    "Outcall",
    "OutcallTrunk",
    "Paging",
    "PagingUser",
    "ParkingLot",
    "PhoneNumber",
    "Pickup",
    "PickupMember",
    "PJSIPTransport",
    "PJSIPTransportOption",
    "Provisioning",
    "Queue",
    "QueueLog",
    "QueueFeatures",
    "QueueMember",
    "QueueSkill",
    "QueueSkillRule",
    "Resolvconf",
    "RightCall",
    "RightCallExten",
    "RightCallMember",
    "SCCPDevice",
    "SCCPGeneralSettings",
    "SCCPLine",
    "Schedule",
    "ScheduleTime",
    "SchedulePath",
    "Session",
    "StatAgent",
    "StatAgentPeriodic",
    "StatCallOnQueue",
    "StatQueue",
    "StatQueuePeriodic",
    "StatSwitchboardQueue",
    "StaticIAX",
    "StaticQueue",
    "StaticVoicemail",
    "StatsConf",
    "StatsConfAgent",
    "StatsConfQueue",
    "StatsConfXivoUser",
    "Switchboard",
    "SwitchboardMemberUser",
    "Tenant",
    "TrunkFeatures",
    "UserExternalApp",
    "UserLine",
    "UserCustom",
    "UserFeatures",
    "UserIAX",
    "Voicemail",
]
