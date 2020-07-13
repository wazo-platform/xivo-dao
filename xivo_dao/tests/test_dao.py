# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import datetime
import itertools
import logging
import os
import random
import unittest
import time
import string
import uuid
import six

from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from xivo.debug import trace_duration

from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.application import Application
from xivo_dao.alchemy.application_dest_node import ApplicationDestNode
from xivo_dao.alchemy.asterisk_file import AsteriskFile
from xivo_dao.alchemy.asterisk_file_section import AsteriskFileSection
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.call_log_participant import CallLogParticipant
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_type import FuncKeyType
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.infos import Infos
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.moh import MOH
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queueinfo import QueueInfo
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillcat import QueueSkillCat
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.rightcallmember import RightCallMember as CallPermissionAssociation
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.helpers import db_manager
from xivo_dao.helpers.db_manager import Base

logger = logging.getLogger(__name__)

_create_tables = True

TEST_DB_URL = os.getenv('XIVO_TEST_DB_URL', 'postgresql://asterisk:asterisk@localhost/asterisktest')
DEFAULT_TENANT = '4dc2a55e-e83a-42ca-b3ca-87d3ff04ddaf'


def expensive_setup():
    global _create_tables
    if _create_tables and (os.environ.get('CREATE_TABLES', '1') == '1'):
        _init_tables()
        _create_tables = False


@trace_duration
def _init_tables():
    logger.debug("Cleaning tables")
    Base.metadata.reflect()
    logger.debug("drop all tables")
    Base.metadata.drop_all()
    logger.debug("create all tables")
    Base.metadata.create_all()
    logger.debug("Tables cleaned")


Session = sessionmaker()

engine = None


class ItemInserter(object):

    def __init__(self, session, tenant_uuid=None):
        self.session = session

        if tenant_uuid:
            self.default_tenant = Tenant(uuid=tenant_uuid)

    def add_user_line_with_exten(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('email', None)
        kwargs.setdefault('callerid', '"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('exten', '%s' % random.randint(1000, 1999))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)
        kwargs.setdefault('musiconhold', 'default')
        kwargs.setdefault('agentid', None)
        kwargs.setdefault('mobilephonenumber', '')
        kwargs.setdefault('description', '')
        kwargs.setdefault('userfield', '')
        kwargs.setdefault('endpoint_sip_id', None)
        kwargs.setdefault('endpoint_sccp_id', None)
        kwargs.setdefault('endpoint_custom_id', None)
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             email=kwargs['email'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'],
                             musiconhold=kwargs['musiconhold'],
                             agentid=kwargs['agentid'],
                             mobilephonenumber=kwargs['mobilephonenumber'],
                             userfield=kwargs['userfield'],
                             description=kwargs['description'],
                             tenant_uuid=kwargs['tenant_uuid'])
        line = self.add_line(context=kwargs['context'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'],
                             endpoint_sip_id=kwargs['endpoint_sip_id'],
                             endpoint_sccp_id=kwargs['endpoint_sccp_id'],
                             endpoint_custom_id=kwargs['endpoint_custom_id'])
        extension = self.add_extension(exten=kwargs['exten'],
                                       context=kwargs['context'],
                                       typeval=user.id)
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id)
        self.add_line_extension(line_id=line.id,
                                extension_id=extension.id)

        user_line.user = user
        user_line.line = line
        user_line.extension = extension

        return user_line

    def add_user_line_with_queue_member(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('callerid', '"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)
        kwargs.setdefault('musiconhold', 'default')
        kwargs.setdefault('agentid', None)
        kwargs.setdefault('mobilephonenumber', '')
        kwargs.setdefault('description', '')
        kwargs.setdefault('userfield', '')

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'],
                             musiconhold=kwargs['musiconhold'],
                             agentid=kwargs['agentid'],
                             mobilephonenumber=kwargs['mobilephonenumber'],
                             userfield=kwargs['userfield'],
                             description=kwargs['description'])
        line = self.add_line(context=kwargs['context'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'])
        self.add_queue_member(userid=user.id,
                              usertype='user')
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id)

        user_line.user = user
        user_line.line = line

        return user_line

    def add_user_line_without_exten(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('callerid', '"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)
        kwargs.setdefault('agentid', None)
        kwargs.setdefault('mobilephonenumber', '+14184765458')

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'],
                             mobilephonenumber=kwargs['mobilephonenumber'],
                             agentid=kwargs['agentid'])
        line = self.add_line(context=kwargs['context'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'])
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id)

        user_line.user = user
        user_line.line = line

        return user_line

    def add_user_line_without_user(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('provisioningid', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('device', 1)

        kwargs.setdefault('exten', None)
        kwargs.setdefault('type', 'user')

        line = self.add_line(name=kwargs['name'],
                             context=kwargs['context'],
                             provisioningid=kwargs['provisioningid'],
                             device=kwargs['device'])
        extension = self.add_extension(exten=kwargs['exten'],
                                       context=kwargs['context'],
                                       type=kwargs['type'])
        line_extension = self.add_line_extension(line_id=line.id,
                                                 extension_id=extension.id)

        line_extension.extension = extension
        line_extension.line = line

        return line_extension

    def add_endpoint_sip(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        kwargs.setdefault('display_name', self._random_name())
        endpoint_sip = EndpointSIP(**kwargs)
        self.add_me(endpoint_sip)
        return endpoint_sip

    def add_line(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('provisioningid', int(''.join(random.choice('123456789') for _ in range(6))))

        line = LineFeatures(**kwargs)
        self.add_me(line)
        return line

    def add_call_permission(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        call_permission = CallPermission(**kwargs)
        self.session.add(call_permission)
        self.session.flush()
        return call_permission

    def add_user_call_permission_with_user_and_call_permission(self):
        user = self.add_user()
        call_permission = self.add_call_permission()
        user_call_permission = self.add_user_call_permission(user_id=user.id, call_permission_id=call_permission.id)
        user_call_permission.user = user
        user_call_permission.call_permission = call_permission
        return user_call_permission

    def add_user_call_permission(self, **kwargs):
        kwargs.setdefault('type', 'user')
        user_call_permission = CallPermissionAssociation(**kwargs)
        self.add_me(user_call_permission)
        return user_call_permission

    def add_group_call_permission(self, **kwargs):
        kwargs.setdefault('type', 'group')
        group_call_permission = CallPermissionAssociation(**kwargs)
        self.add_me(group_call_permission)
        return group_call_permission

    def add_incall_schedule(self, **kwargs):
        kwargs.setdefault('path', 'incall')
        incall_schedule = SchedulePath(**kwargs)
        self.add_me(incall_schedule)
        return incall_schedule

    def add_context(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        kwargs.setdefault('description', 'Auto create context')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        context = Context(**kwargs)
        self.add_me(context)
        return context

    def add_context_include(self, **kwargs):
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('include', self._random_name())
        kwargs.setdefault('priority', 0)

        context_include = ContextInclude(**kwargs)
        self.add_me(context_include)
        return context_include

    def add_context_number(self, **kwargs):
        kwargs.setdefault('type', 'user')
        context_number = ContextNumbers(**kwargs)
        self.add_me(context_number)
        return context_number

    def add_context_member(self, **kwargs):
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('type', 'user')
        kwargs.setdefault('varname', 'context')

        context_member = ContextMember(**kwargs)
        self.add_me(context_member)
        return context_member

    def add_user_line(self, **kwargs):
        kwargs.setdefault('main_user', True)
        kwargs.setdefault('main_line', True)

        user_line = UserLine(**kwargs)
        self.add_me(user_line)
        return user_line

    def add_line_extension(self, **kwargs):
        kwargs.setdefault('main_extension', True)

        line_extension = LineExtension(**kwargs)
        self.add_me(line_extension)
        return line_extension

    def add_extension(self, **kwargs):
        kwargs.setdefault('exten', '%s' % self._generate_random_exten())
        kwargs.setdefault('type', 'user')
        kwargs.setdefault('context', 'default')

        extension = Extension(**kwargs)
        self.add_me(extension)
        return extension

    def _generate_random_exten(self):
        extensions = self.session.query(Extension).all()
        extens = [extension.exten for extension in extensions]
        return self._random_exten(extens)

    def _random_exten(self, extens):
        exten = str(random.randint(1000, 4000))
        if exten in extens:
            return self._random_exten(extens)
        return exten

    def add_ivr(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        kwargs.setdefault('menu_sound', 'silence')
        ivr = IVR(**kwargs)
        self.add_me(ivr)
        return ivr

    def add_ivr_choice(self, **kwargs):
        kwargs.setdefault('exten', '42')
        ivr_choice = IVRChoice(**kwargs)
        self.add_me(ivr_choice)
        return ivr_choice

    def add_incall(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        incall = Incall(**kwargs)
        self.add_me(incall)
        return incall

    def add_outcall(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice(string.ascii_lowercase) for _ in range(6)))
        kwargs.setdefault('context', 'to-extern')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        outcall = Outcall(**kwargs)
        self.add_me(outcall)
        return outcall

    def add_outcall_call_permission(self, **kwargs):
        kwargs.setdefault('type', 'outcall')
        outcall_call_permission = CallPermissionAssociation(**kwargs)
        self.add_me(outcall_call_permission)
        return outcall_call_permission

    def add_outcall_schedule(self, **kwargs):
        kwargs.setdefault('path', 'outcall')
        outcall_schedule = SchedulePath(**kwargs)
        self.add_me(outcall_schedule)
        return outcall_schedule

    def add_user(self, **kwargs):
        if 'func_key_private_template_id' not in kwargs:
            func_key_template = self.add_func_key_template(private=True)
            kwargs['func_key_private_template_id'] = func_key_template.id

        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        kwargs.setdefault('firstname', 'John')

        fullname = kwargs['firstname']
        if 'lastname' in kwargs:
            fullname += " " + kwargs['lastname']

        kwargs.setdefault('callerid', '"{}"'.format(fullname))
        user = UserFeatures(**kwargs)
        self.add_me(user)
        return user

    def add_agent(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('number', ''.join(random.choice('123456789') for _ in range(6)))
        kwargs.setdefault('passwd', '')
        kwargs.setdefault('language', random.choice(['fr_FR', 'en_US']))
        kwargs.setdefault('description', 'description')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        agent = AgentFeatures(**kwargs)
        self.add_me(agent)
        return agent

    def add_agent_login_status(self, **kwargs):
        kwargs.setdefault('agent_id', self._generate_int())
        kwargs.setdefault('agent_number', '1234')
        kwargs.setdefault('extension', ''.join(random.choice('123456789') for _ in range(6)))
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('interface', self._random_name())
        kwargs.setdefault('state_interface', '')
        agent_login_status = AgentLoginStatus(**kwargs)
        self.add_me(agent_login_status)
        return agent_login_status

    def add_group(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        group = GroupFeatures(**kwargs)
        self.add_me(group)
        return group

    def add_group_schedule(self, **kwargs):
        kwargs.setdefault('path', 'group')
        group_schedule = SchedulePath(**kwargs)
        self.add_me(group_schedule)
        return group_schedule

    def add_queuefeatures(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        queuefeatures = QueueFeatures(**kwargs)
        self.add_me(queuefeatures)
        return queuefeatures

    def add_queue_info(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('call_time_t', int(time.time()))
        kwargs.setdefault('queue_name', self._random_name())
        kwargs.setdefault('hold_time', self._generate_int())
        kwargs.setdefault('talk_time', self._generate_int())
        kwargs.setdefault('caller_uniqueid', str(self._generate_int()))
        qi = QueueInfo(**kwargs)
        self.add_me(qi)
        return qi

    def add_meetmefeatures(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('meetmeid', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('confno', ''.join(random.choice('0123456789') for _ in range(6)))
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('admin_identification', 'all')
        kwargs.setdefault('admin_mode', 'all')
        kwargs.setdefault('admin_announcejoinleave', 'no')
        kwargs.setdefault('user_mode', 'all')
        kwargs.setdefault('user_announcejoinleave', 'no')
        kwargs.setdefault('emailbody', '')
        kwargs.setdefault('description', '')
        meetmefeatures = MeetmeFeatures(**kwargs)
        self.add_me(meetmefeatures)
        return meetmefeatures

    def add_conference(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        conference = Conference(**kwargs)
        self.add_me(conference)
        return conference

    def add_queue(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        queue = Queue(**kwargs)
        self.add_me(queue)
        return queue

    def add_agent_queue_skill(self, **kwargs):
        kwargs.setdefault('skillid', self._generate_int())
        kwargs.setdefault('agentid', self._generate_int())
        agent_skill = AgentQueueSkill(**kwargs)
        self.add_me(agent_skill)
        return agent_skill

    def add_queue_skill(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('description', '')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        queue_skill = QueueSkill(**kwargs)
        self.add_me(queue_skill)
        return queue_skill

    def add_queue_skill_category(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        skill_category = QueueSkillCat(**kwargs)
        self.add_me(skill_category)
        return skill_category

    def add_queue_skill_rule(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        queue_skill_rule = QueueSkillRule(**kwargs)
        self.add_me(queue_skill_rule)
        return queue_skill_rule

    def add_queue_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'queues.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_queue = StaticQueue(**kwargs)
        self.add_me(static_queue)
        return static_queue

    def add_queue_member(self, **kwargs):
        kwargs.setdefault('queue_name', self._random_name())
        kwargs.setdefault('interface', self._random_name())
        kwargs.setdefault('usertype', random.choice(['user', 'agent']))
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        kwargs.setdefault('channel', self._random_name())
        kwargs.setdefault('userid', self._generate_int())

        queue_member = QueueMember(**kwargs)
        self.add_me(queue_member)
        return queue_member

    def add_pickup(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        pickup = Pickup(**kwargs)
        self.add_me(pickup)
        return pickup

    def add_pickup_member(self, **kwargs):
        kwargs.setdefault('pickupid', self._generate_int())
        kwargs.setdefault('category', random.choice(['pickup', 'member']))
        kwargs.setdefault('membertype', random.choice(['group', 'queue', 'user']))
        kwargs.setdefault('memberid', self._generate_int())

        pickup_member = PickupMember(**kwargs)
        self.add_me(pickup_member)
        return pickup_member

    def add_dialpattern(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('type', 'outcall')
        kwargs.setdefault('typeid', self._generate_int())
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        dialpattern = DialPattern(**kwargs)
        self.add_me(dialpattern)
        return dialpattern

    def add_dialaction(self, **kwargs):
        kwargs.setdefault('event', 'never mind')
        kwargs.setdefault('category', 'incall')
        kwargs.setdefault('categoryval', '1')
        kwargs.setdefault('action', 'none')
        dialaction = Dialaction(**kwargs)
        self.add_me(dialaction)
        return dialaction

    def add_tenant(self, **kwargs):
        tenant = Tenant(**kwargs)
        self.add_me(tenant)
        return tenant

    def add_transport(self, **kwargs):
        kwargs.setdefault('name', 'transport')
        transport = PJSIPTransport(**kwargs)
        self.add_me(transport)
        return transport

    def add_trunk(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        trunk = TrunkFeatures(**kwargs)
        self.add_me(trunk)
        return trunk

    def add_usersip(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('type', 'friend')
        kwargs.setdefault('category', 'user')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        usersip = UserSIP(**kwargs)
        self.add_me(usersip)
        return usersip

    def add_useriax(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('type', 'friend')
        kwargs.setdefault('category', 'user')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        useriax = UserIAX(**kwargs)
        self.add_me(useriax)
        return useriax

    def add_usercustom(self, **kwargs):
        kwargs.setdefault('interface', self._random_name())
        kwargs.setdefault('category', 'user')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        usercustom = UserCustom(**kwargs)
        self.add_me(usercustom)
        return usercustom

    def add_sccpdevice(self, **kwargs):
        kwargs.setdefault('name', 'SEP001122334455')
        kwargs.setdefault('device', 'SEP001122334455')
        kwargs.setdefault('line', '1000')
        kwargs.setdefault('id', self._generate_int())

        sccpdevice = SCCPDeviceSchema(**kwargs)
        self.add_me(sccpdevice)
        return sccpdevice

    def add_sccpline(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('cid_name', 'Tester One')
        kwargs.setdefault('cid_num', '1234')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)

        sccpline = SCCPLine(**kwargs)
        self.add_me(sccpline)
        return sccpline

    def add_function_key_to_user(self, **kwargs):
        kwargs.setdefault('iduserfeatures', self._generate_int())
        kwargs.setdefault('fknum', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('supervision', 0)
        kwargs.setdefault('label', 'toto')
        kwargs.setdefault('typeextenumbersright', 'user')
        kwargs.setdefault('typeextenumbers', None)
        kwargs.setdefault('typevalextenumbers', None)
        kwargs.setdefault('progfunckey', '1')

        phone_func_key = PhoneFunckey(**kwargs)
        self.add_me(phone_func_key)
        return phone_func_key

    def add_sccp_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('option_name', 'directmedia')
        kwargs.setdefault('option_value', 'no')

        sccp_general_settings = SCCPGeneralSettings(**kwargs)
        self.add_me(sccp_general_settings)
        return sccp_general_settings

    def add_cel(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('eventtype', 'eventtype')
        kwargs.setdefault('eventtime', datetime.datetime.now())
        kwargs.setdefault('userdeftype', 'userdeftype')
        kwargs.setdefault('cid_name', 'cid_name')
        kwargs.setdefault('cid_num', 'cid_num')
        kwargs.setdefault('cid_ani', 'cid_ani')
        kwargs.setdefault('cid_rdnis', 'cid_rdnis')
        kwargs.setdefault('cid_dnid', 'cid_dnid')
        kwargs.setdefault('exten', 'exten')
        kwargs.setdefault('context', 'context')
        kwargs.setdefault('channame', 'channame')
        kwargs.setdefault('appname', 'appname')
        kwargs.setdefault('appdata', 'appdata')
        kwargs.setdefault('amaflags', 0)
        kwargs.setdefault('accountcode', 'accountcode')
        kwargs.setdefault('peeraccount', 'peeraccount')
        kwargs.setdefault('uniqueid', 'uniqueid')
        kwargs.setdefault('linkedid', 'linkedid')
        kwargs.setdefault('userfield', 'userfield')
        kwargs.setdefault('peer', 'peer')

        cel = CELSchema(**kwargs)
        self.add_me(cel)
        return cel.id

    def add_voicemail(self, **kwargs):
        if not kwargs.get('number'):
            kwargs.setdefault('mailbox', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('context', 'unittest')
        kwargs.setdefault('uniqueid', self._generate_int())

        voicemail = VoicemailSchema(**kwargs)
        self.add_me(voicemail)
        return voicemail

    def link_user_and_voicemail(self, user_row, voicemail_id):
        user_row.voicemailtype = 'asterisk'
        user_row.voicemailid = voicemail_id

        if not user_row.language:
            user_row.language = 'fr_FR'

        self.add_me(user_row)

    def add_moh(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('mode', 'files')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        moh = MOH(**kwargs)
        self.add_me(moh)
        return moh

    def add_iax_callnumberlimits(self, **kwargs):
        kwargs.setdefault('destination', '127.0.0.1')
        kwargs.setdefault('netmask', '255.255.255.255')

        iax_callnumberlimits = IAXCallNumberLimits(**kwargs)
        self.add_me(iax_callnumberlimits)
        return iax_callnumberlimits

    def add_meetme_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'meetme.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_meetme = StaticMeetme(**kwargs)
        self.add_me(static_meetme)
        return static_meetme

    def add_voicemail_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'voicemail.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_voicemail = StaticVoicemail(**kwargs)
        self.add_me(static_voicemail)
        return static_voicemail

    def add_voicemail_zonemessages_settings(self, **kwargs):
        return self.add_voicemail_general_settings(category='zonemessages', **kwargs)

    def add_iax_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'iax.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_iax = StaticIAX(**kwargs)
        self.add_me(static_iax)
        return static_iax

    def add_register_iax(self, **kwargs):
        kwargs.setdefault('var_name', 'register')
        return self.add_iax_general_settings(**kwargs)

    def add_sip_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'sip.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_sip = StaticSIP(**kwargs)
        self.add_me(static_sip)
        return static_sip

    def add_register_sip(self, **kwargs):
        kwargs.setdefault('var_name', 'register')
        return self.add_sip_general_settings(**kwargs)

    def add_asterisk_file(self, **kwargs):
        kwargs.setdefault('name', self._random_name())

        asterisk_file = AsteriskFile(**kwargs)
        self.add_me(asterisk_file)
        return asterisk_file

    def add_asterisk_file_section(self, **kwargs):
        kwargs.setdefault('name', self._random_name())

        asterisk_file_section = AsteriskFileSection(**kwargs)
        self.add_me(asterisk_file_section)
        return asterisk_file_section

    def add_asterisk_file_variable(self, **kwargs):
        kwargs.setdefault('key', 'nat')

        asterisk_file_variable = AsteriskFileVariable(**kwargs)
        self.add_me(asterisk_file_variable)
        return asterisk_file_variable

    def add_func_key(self, **kwargs):
        func_key_row = FuncKey(**kwargs)
        self.add_me(func_key_row)
        return func_key_row

    def add_func_key_template(self, **kwargs):
        func_key_template = FuncKeyTemplate(**kwargs)
        self.add_me(func_key_template)
        return func_key_template

    def add_func_key_type(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', 'speeddial')
        func_key_type_row = FuncKeyType(**kwargs)
        self.add_me(func_key_type_row)
        return func_key_type_row

    def add_func_key_destination_type(self, **kwargs):
        kwargs.setdefault('id', 1)
        kwargs.setdefault('name', 'user')
        destination_type_row = FuncKeyDestinationType(**kwargs)
        self.add_me(destination_type_row)
        return destination_type_row

    def add_schedule(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        schedule = Schedule(**kwargs)
        self.add_me(schedule)
        return schedule

    def add_schedule_time(self, **kwargs):
        schedule_time = ScheduleTime(**kwargs)
        self.add_me(schedule_time)
        return schedule_time

    def add_schedule_path(self, **kwargs):
        kwargs.setdefault('path', 'user')
        kwargs.setdefault('pathid', 0)
        schedule_path = SchedulePath(**kwargs)
        self.add_me(schedule_path)
        return schedule_path

    def add_bsfilter(self, **kwargs):
        kwargs.setdefault('callfrom', 'internal')
        kwargs.setdefault('type', 'bosssecretary')
        kwargs.setdefault('name', 'bsfilter')
        kwargs.setdefault('description', '')
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        callfilter = Callfilter(**kwargs)
        self.add_me(callfilter)
        return callfilter

    def add_call_filter(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('type', 'bosssecretary')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        callfilter = Callfilter(**kwargs)
        self.add_me(callfilter)
        return callfilter

    def add_filter_member(self, filterid, userid, role='boss'):
        member = Callfiltermember(type='user',
                                  typeval=str(userid),
                                  callfilterid=filterid,
                                  bstype=role)
        self.add_me(member)
        return member

    def add_call_filter_member(self, **kwargs):
        kwargs.setdefault('type', 'user')
        kwargs.setdefault('typeval', str(self._generate_int()))
        kwargs.setdefault('bstype', 'boss')
        callfiltermember = Callfiltermember(**kwargs)
        self.add_me(callfiltermember)
        return callfiltermember

    def add_func_key_mapping(self, **kwargs):
        kwargs.setdefault('position', 1)
        func_key_mapping = FuncKeyMapping(**kwargs)
        self.add_me(func_key_mapping)
        return func_key_mapping

    def add_features(self, **kwargs):
        kwargs.setdefault('filename', 'features.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())
        feature = Features(**kwargs)
        self.add_me(feature)
        return feature

    def add_paging(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        paging = Paging(**kwargs)
        self.add_me(paging)
        return paging

    def _generate_paging_number(self):
        pagings = self.session.query(Paging).all()
        numbers = [paging.number for paging in pagings]
        return self._random_exten(numbers)

    def add_paging_user(self, **kwargs):
        kwargs.setdefault('caller', 0)
        paging_user = PagingUser(**kwargs)
        self.add_me(paging_user)
        return paging_user

    def add_parking_lot(self, **kwargs):
        kwargs.setdefault('slots_start', '701')
        kwargs.setdefault('slots_end', '750')
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        parking_lot = ParkingLot(**kwargs)
        self.add_me(parking_lot)
        return parking_lot

    def add_accessfeatures(self, host, **kwargs):
        kwargs.setdefault('feature', 'phonebook')
        accessfeature = AccessFeatures(host=host, **kwargs)
        self.add_me(accessfeature)
        return accessfeature

    def add_callerid(self, **kwargs):
        kwargs.setdefault('type', 'group')
        kwargs.setdefault('typeval', self._generate_int())
        callerid = Callerid(**kwargs)
        self.add_me(callerid)
        return callerid

    def add_infos(self, **kwargs):
        kwargs.setdefault('wazo_version', 'dev')
        infos = Infos(**kwargs)
        self.add_me(infos)
        return infos

    def add_switchboard(self, **kwargs):
        kwargs.setdefault('uuid', str(uuid.uuid4()))
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        kwargs.setdefault('name', self._random_name())
        switchboard = Switchboard(**kwargs)
        self.add_me(switchboard)
        return switchboard

    def add_call_log(self, **kwargs):
        kwargs.setdefault('date', datetime.datetime.now())
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        call_log = CallLog(**kwargs)
        self.add_me(call_log)
        return call_log

    def add_call_log_participant(self, **kwargs):
        kwargs.setdefault('role', 'source')
        call_log_participant = CallLogParticipant(**kwargs)
        self.add_me(call_log_participant)
        return call_log_participant

    def add_application(self, **kwargs):
        kwargs.setdefault('tenant_uuid', self.default_tenant.uuid)
        application = Application(**kwargs)
        self.add_me(application)
        return application

    def add_application_dest_node(self, **kwargs):
        kwargs.setdefault('type_', 'holding')
        application = ApplicationDestNode(**kwargs)
        self.add_me(application)
        return application

    def add_me(self, obj):
        self.session.add(obj)
        self.session.flush()

    def add_me_all(self, obj_list):
        self.session.add_all(obj_list)
        self.session.flush()

    _generate_int_init = itertools.count(1)

    def _generate_int(self):
        return six.next(self._generate_int_init)

    def _random_name(self, length=6):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


class DAOTestCase(unittest.TestCase, ItemInserter):

    @classmethod
    def setUpClass(cls):
        global engine
        if not engine:
            # engine = create_engine(TEST_DB_URL, poolclass=StaticPool, echo=True)
            engine = create_engine(TEST_DB_URL, poolclass=StaticPool)

        cls.engine = Base.metadata.bind = engine
        expensive_setup()

    def setUp(self):
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()

        db_manager.Session.configure(bind=self.connection)
        self.session = db_manager.Session

        self.session.begin_nested()

        self.default_tenant = self.add_tenant(uuid=DEFAULT_TENANT)

        @event.listens_for(self.session, 'after_transaction_end')
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.expire_all()
                session.begin_nested()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        self.trans.rollback()
