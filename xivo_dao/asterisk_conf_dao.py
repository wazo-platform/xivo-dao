# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple

from sqlalchemy import bindparam
from sqlalchemy.ext import baked
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import and_, cast, func, literal, or_, true
from sqlalchemy.types import Integer

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.endpoint_sip import EndpointSIP, EndpointSIPTemplate
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.db_manager import daosession


class Member(NamedTuple):
    interface: str
    penalty: str
    name: str
    state_interface: str


@daosession
def find_sccp_general_settings(session):
    rows = session.query(SCCPGeneralSettings).all()

    voicemail_consult_exten = (
        session.query(
            literal('vmexten').label('option_name'),
            FeatureExtension.exten.label('option_value'),
        )
        .filter(
            and_(
                FeatureExtension.feature == 'vmusermsg',
            )
        )
        .first()
    )

    res = [
        {
            'option_name': row.option_name,
            'option_value': row.option_value,
        }
        for row in rows
    ]

    res.append(
        {
            'option_name': voicemail_consult_exten.option_name,
            'option_value': voicemail_consult_exten.option_value,
        }
    )

    return res


@daosession
def find_sccp_line_settings(session):
    sccp_pickup_members = find_pickup_members('sccp')

    def line_config(*args):
        (
            endpoint_sccp_id,
            tenant_uuid,
            name,
            cid_name,
            cid_num,
            allow,
            disallow,
            language,
            user_id,
            context,
            number,
            uuid,
            enable_online_recording,
            simultcalls,
        ) = args

        line = {
            'id': endpoint_sccp_id,
            'name': name,
            'cid_name': cid_name,
            'cid_num': cid_num,
            'user_id': user_id,
            'number': number,
            'context': context,
            'language': language,
            'uuid': uuid,
            'tenant_uuid': tenant_uuid,
            'enable_online_recording': enable_online_recording,
            'simultcalls': simultcalls,
        }

        if allow:
            line['allow'] = allow
        if disallow:
            line['disallow'] = disallow

        line.update(sccp_pickup_members.get(endpoint_sccp_id, {}))

        return line

    rows = (
        session.query(
            SCCPLine.id,
            SCCPLine.tenant_uuid,
            SCCPLine.name,
            SCCPLine.cid_name,
            SCCPLine.cid_num,
            SCCPLine.allow,
            SCCPLine.disallow,
            UserFeatures.language,
            UserLine.user_id,
            LineFeatures.context,
            Extension.exten,
            UserFeatures.uuid,
            UserFeatures.enableonlinerec,
            UserFeatures.simultcalls,
        )
        .join(
            LineFeatures,
            and_(
                LineFeatures.endpoint_sccp_id == SCCPLine.id,
            ),
        )
        .join(
            UserLine,
            UserLine.line_id == LineFeatures.id,
        )
        .join(
            UserFeatures,
            and_(
                UserFeatures.id == UserLine.user_id,
                UserLine.main_user.is_(True),
            ),
        )
        .join(
            LineExtension,
            and_(
                LineFeatures.id == LineExtension.line_id,
                LineExtension.main_extension.is_(True),
            ),
        )
        .join(
            Extension,
            LineExtension.extension_id == Extension.id,
        )
        .filter(LineFeatures.commented == 0)
        .all()
    )

    for row in rows:
        yield line_config(*row)


@daosession
def find_sccp_device_settings(session):
    query = (
        session.query(
            SCCPDevice,
            Voicemail.mailbox,
        )
        .outerjoin(
            SCCPLine,
            SCCPLine.name == SCCPDevice.line,
        )
        .outerjoin(
            LineFeatures,
            and_(
                LineFeatures.endpoint_sccp_id == SCCPLine.id,
            ),
        )
        .outerjoin(
            UserLine,
            and_(
                UserLine.line_id == LineFeatures.id,
                UserLine.main_user.is_(True),
            ),
        )
        .outerjoin(
            UserFeatures,
            UserFeatures.id == UserLine.user_id,
        )
        .outerjoin(
            Voicemail,
            Voicemail.uniqueid == UserFeatures.voicemailid,
        )
    )

    devices = []
    for row in query:
        device = row.SCCPDevice.todict()
        device['voicemail'] = row.mailbox
        devices.append(device)

    return devices


@daosession
def find_sccp_speeddial_settings(session):
    invalid_chars = '\n\r\t;'
    query = (
        session.query(
            FuncKeyMapping.position.label('fknum'),
            func.translate(FuncKeyMapping.label, invalid_chars, '').label('label'),
            cast(FuncKeyMapping.blf, Integer).label('supervision'),
            func.translate(FuncKeyDestCustom.exten, invalid_chars, '').label('exten'),
            UserFeatures.id.label('user_id'),
            SCCPDevice.device.label('device'),
        )
        .join(
            UserFeatures,
            FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
        )
        .join(
            FuncKeyDestCustom,
            FuncKeyDestCustom.func_key_id == FuncKeyMapping.func_key_id,
        )
        .join(
            UserLine,
            and_(
                UserLine.user_id == UserFeatures.id,
                UserLine.main_user.is_(True),
            ),
        )
        .join(
            LineFeatures,
            UserLine.line_id == LineFeatures.id,
        )
        .join(
            SCCPLine,
            and_(
                LineFeatures.endpoint_sccp_id == SCCPLine.id,
            ),
        )
        .join(
            SCCPDevice,
            SCCPLine.name == SCCPDevice.line,
        )
        .filter(LineFeatures.commented == 0)
    )

    return [
        {
            'exten': row.exten,
            'fknum': row.fknum,
            'label': row.label,
            'supervision': row.supervision,
            'user_id': row.user_id,
            'device': row.device,
        }
        for row in query
    ]


@daosession
def find_features_settings(session):
    rows = (
        session.query(
            Features.category,
            Features.var_name,
            Features.var_val,
        )
        .filter(
            and_(
                Features.commented == 0,
                or_(
                    Features.category == 'general',
                    Features.category == 'featuremap',
                    Features.category == 'applicationmap',
                ),
            )
        )
        .all()
    )

    general_options = []
    featuremap_options = []
    applicationmap_options = []
    for row in rows:
        option = (row.var_name, row.var_val)
        if row.category == 'general':
            general_options.append(option)
        elif row.category == 'applicationmap':
            applicationmap_options.append(option)
        elif row.category == 'featuremap':
            featuremap_options.append(option)
            if row.var_name == 'disconnect':
                option = ('atxferabort', row.var_val)
                general_options.append(option)

    return {
        'general_options': general_options,
        'featuremap_options': featuremap_options,
        'applicationmap_options': applicationmap_options,
    }


@daosession
def find_exten_conferences_settings(session, context_name):
    rows = (
        session.query(Extension.exten)
        .filter(
            and_(
                Extension.type == 'conference',
                Extension.context == context_name,
                Extension.commented == 0,
            )
        )
        .order_by('exten')
        .all()
    )
    return [{'exten': row[0]} for row in rows]


@daosession
def find_exten_xivofeatures_setting(session):
    rows = (
        session.query(FeatureExtension)
        .filter(
            FeatureExtension.enabled == true(),
        )
        .order_by('exten')
        .all()
    )

    return [row.todict() for row in rows]


@daosession
def find_extenfeatures_settings(session, features):
    query = (
        session.query(FeatureExtension)
        .filter(
            and_(
                FeatureExtension.feature.in_(features),
            )
        )
        .order_by('exten')
    )

    return query.all()


exten_settings_bakery = baked.bakery()
exten_settings_query = exten_settings_bakery(
    lambda s: s.query(
        Extension,
    )
    .outerjoin(
        LineExtension,
        Extension.id == LineExtension.extension_id,
    )
    .outerjoin(
        LineFeatures,
        LineFeatures.id == LineExtension.line_id,
    )
    .filter(
        and_(
            Extension.commented == 0,
            Extension.typeval != '0',
            Extension.type != 'parking',
            or_(
                LineExtension.line_id.is_(None),
                LineFeatures.commented == 0,
            ),
        )
    )
    .order_by('exten')
)
exten_settings_query += lambda q: q.filter(Extension.context == bindparam('context'))


@daosession
def find_exten_settings(session, context_name):
    rows = exten_settings_query(session).params(context=context_name).all()
    return [
        dict(tenant_uuid=row.context_rel.tenant_uuid, **row.todict()) for row in rows
    ]


@daosession
def find_context_settings(session):
    rows = session.query(Context).filter(Context.commented == 0).order_by('name').all()

    return [row.todict() for row in rows]


context_include_bakery = baked.bakery()
context_include_query = context_include_bakery(
    lambda s: s.query(ContextInclude).order_by('priority')
)
context_include_query += lambda q: q.filter(
    ContextInclude.context == bindparam('context')
)


@daosession
def find_contextincludes_settings(session, context_name):
    rows = context_include_query(session).params(context=context_name).all()
    return [row.todict() for row in rows]


@daosession
def find_voicemail_activated(session):
    rows = session.query(Voicemail).filter(Voicemail.commented == 0).all()

    return [row.todict() for row in rows]


@daosession
def find_voicemail_general_settings(session):
    rows = session.query(StaticVoicemail).filter(StaticVoicemail.commented == 0).all()

    res = []
    for row in rows:
        res.append(
            {
                'category': row.category,
                'var_name': row.var_name,
                'var_val': row.var_val,
            }
        )

    return res


class _SIPEndpointResolver:
    def __init__(self, endpoint_config, parents):
        self._endpoint_config = endpoint_config
        self._base_config = self._endpoint_to_dict(self._endpoint_config)
        self._parents = parents
        self.template = endpoint_config.template

        self._body = None

        self._aor_section = None
        self._auth_section = None
        self._endpoint_section = None
        self._identify_section = None
        self._outbound_auth_section = None
        self._registration_section = None
        self._registration_outbound_auth_section = None

    def get_aor_section(self):
        return self._get_section('aor')

    def get_auth_section(self):
        return self._get_section('auth')

    def get_endpoint_section(self):
        return self._get_section('endpoint')

    def get_identify_section(self):
        return self._get_section('identify')

    def get_outbound_auth_section(self):
        return self._get_section('outbound_auth')

    def get_registration_section(self):
        return self._get_section('registration')

    def get_registration_outbound_auth_section(self):
        return self._get_section('registration_outbound_auth')

    def _get_section(self, name):
        field_name = f'_{name}_section'
        if getattr(self, field_name) is None:
            build_method_name = f'_build_{name}_section'
            build_method = getattr(self, build_method_name)
            section = build_method()
            setattr(self, field_name, section)
        return getattr(self, field_name)

    def resolve(self):
        if self._body is None:
            self._body = self._canonicalize_config(
                {
                    'uuid': self._endpoint_config.uuid,
                    'name': self._endpoint_config.name,
                    'label': self._endpoint_config.label,
                    'template': self._endpoint_config.template,
                    'asterisk_id': self._endpoint_config.asterisk_id,
                    'aor_section_options': self.get_aor_section(),
                    'auth_section_options': self.get_auth_section(),
                    'endpoint_section_options': self.get_endpoint_section(),
                    'identify_section_options': self.get_identify_section(),
                    'outbound_auth_section_options': self.get_outbound_auth_section(),
                    'registration_section_options': self.get_registration_section(),
                    'registration_outbound_auth_section_options': self.get_registration_outbound_auth_section(),
                }
            )

        return self._body

    def _add_parent_options(self, section_name, options=None):
        options = options or []
        for parent in self._iterover_parents():
            method_name = f'get_{section_name}_section'
            method = getattr(parent, method_name)
            for option in method():
                options.append(option)

        field_name = f'{section_name}_section_options'
        for option in self._base_config.get(field_name, []):
            options.append(option)

        return options

    def _build_aor_section(self):
        options = self._add_parent_options('aor')
        if options:
            options.append(('type', 'aor'))
        return options

    def _build_auth_section(self):
        options = self._add_parent_options('auth')
        if options:
            options.append(('type', 'auth'))
        return options

    def _build_endpoint_section(self):
        options = self._default_endpoint_section()
        options = self._add_parent_options('endpoint', options)

        if self._endpoint_config.transport_uuid:
            options.append(('transport', self._endpoint_config.transport.name))

        original_caller_id = None
        for key, value in options:
            if key == 'callerid':
                original_caller_id = value
        if original_caller_id:
            options.append(('set_var', f'XIVO_ORIGINAL_CALLER_ID={original_caller_id}'))

        aor_options = self.get_aor_section()
        if aor_options:
            options.append(('aors', self._endpoint_config.name))

        auth_options = self.get_auth_section()
        if auth_options:
            options.append(('auth', self._endpoint_config.name))

        if options:
            options.append(('type', 'endpoint'))

            if self.get_outbound_auth_section():
                options.append(
                    ('outbound_auth', f'outbound_auth_{self._endpoint_config.name}')
                )

        return options

    def _build_identify_section(self):
        options = self._add_parent_options('identify')
        if options:
            options.append(('type', 'identify'))
            options.append(('endpoint', self._endpoint_config.name))
        return options

    def _build_outbound_auth_section(self):
        options = self._add_parent_options('outbound_auth')
        if options:
            options.append(('type', 'auth'))
        return options

    def _build_registration_section(self):
        options = self._add_parent_options('registration')
        if options:
            options.append(('type', 'registration'))
            options.append(('endpoint', self._endpoint_config.name))
            if self.get_registration_outbound_auth_section():
                options.append(
                    ('outbound_auth', f'auth_reg_{self._endpoint_config.name}')
                )
        return options

    def _build_registration_outbound_auth_section(self):
        options = self._add_parent_options('registration_outbound_auth')
        if options:
            options.append(('type', 'auth'))
        return options

    def _default_endpoint_section(self):
        return [
            ('set_var', f'__WAZO_TENANT_UUID={self._endpoint_config.tenant_uuid}'),
        ]

    def _add_mixmonitor_options(self, tenant, options):
        mixmonitor_options = "p"
        if start_announce := tenant['record_start_announcement']:
            mixmonitor_options += f"({start_announce})"

        mixmonitor_options += "P"
        if stop_announce := tenant['record_stop_announcement']:
            mixmonitor_options += f"({stop_announce})"

        options.append(('set_var', f'__WAZO_MIXMONITOR_OPTIONS={mixmonitor_options}'))
        return options

    def _iterover_parents(self):
        for template in self._endpoint_config.templates:
            yield self._parents[template.uuid]

    @staticmethod
    def _canonicalize_config(config):
        sections = [
            'aor_section_options',
            'auth_section_options',
            'endpoint_section_options',
            'registration_section_options',
            'identify_section_options',
            'registration_outbound_auth_section_options',
            'outbound_auth_section_options',
        ]
        repeatable_options = [
            'set_var',
            'match',
        ]

        for section in sections:
            accumulator = {}
            repeated_options = []
            for key, value in config.get(section, []):
                if key in repeatable_options:
                    if [key, value] not in repeated_options:
                        repeated_options.append([key, value])
                else:
                    accumulator[key] = value
            config[section] = list(accumulator.items()) + repeated_options

        return config

    @staticmethod
    def _endpoint_to_dict(endpoint):
        return {
            'uuid': endpoint.uuid,
            'name': endpoint.name,
            'label': endpoint.label,
            'aor_section_options': list(endpoint.aor_section_options),
            'auth_section_options': list(endpoint.auth_section_options),
            'endpoint_section_options': list(endpoint.endpoint_section_options),
            'registration_section_options': list(endpoint.registration_section_options),
            'registration_outbound_auth_section_options': list(
                endpoint.registration_outbound_auth_section_options
            ),
            'identify_section_options': list(endpoint.identify_section_options),
            'outbound_auth_section_options': list(
                endpoint.outbound_auth_section_options
            ),
            'template': endpoint.template,
            'asterisk_id': endpoint.asterisk_id,
        }


class _EndpointSIPMeetingResolver(_SIPEndpointResolver):
    def __init__(self, meeting, parents, tenants_settings):
        super().__init__(meeting.guest_endpoint_sip, parents)
        self._meeting = meeting
        self._tenants_settings = tenants_settings

    def _default_endpoint_section(self):
        options = super()._default_endpoint_section() + [
            ('set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'),
            ('set_var', f'WAZO_MEETING_UUID={self._meeting.uuid}'),
            ('set_var', f'WAZO_MEETING_NAME={self._meeting.name}'),
        ]
        options = self._add_mixmonitor_options(
            self._tenants_settings[self._endpoint_config.tenant_uuid], options
        )
        return options


class _EndpointSIPTrunkResolver(_SIPEndpointResolver):
    def __init__(self, trunk, parents, tenants_settings):
        super().__init__(trunk.endpoint_sip, parents)
        self._trunk = trunk
        self._tenants_settings = tenants_settings

    def _default_endpoint_section(self):
        options = super()._default_endpoint_section() + [
            ('set_var', 'WAZO_PAI_FORMAT='),
        ]

        if self._trunk.context:
            options.append(('context', self._trunk.context))

        options = self._add_mixmonitor_options(
            self._tenants_settings[self._endpoint_config.tenant_uuid], options
        )
        return options


class _EndpointSIPLineResolver(_SIPEndpointResolver):
    def __init__(self, line, parents, pickup_members, tenants_settings):
        super().__init__(line.endpoint_sip, parents)
        self._line = line
        self._pickup_members = pickup_members
        self._tenants_settings = tenants_settings

    def _add_mailboxes(self, options):
        mailboxes = []
        for user in self._line.users:
            if user.voicemail:
                mailboxes.append(f'{user.voicemail.number}@{user.voicemail.context}')
        if mailboxes:
            options.append(('mailboxes', ','.join(mailboxes)))
        return options

    def _build_aor_section(self):
        options = super()._build_aor_section()
        options = self._add_mailboxes(options)

        if options:
            options.append(('type', 'aor'))

        return options

    def _default_endpoint_section(self):
        options = super()._default_endpoint_section() + [
            ('set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'),
            ('set_var', f'WAZO_LINE_ID={self._line.id}'),
        ]

        context_name = self._line.context
        if self._line.application_uuid:
            outgoing_context = f'stasis-wazo-app-{self._line.application_uuid}'
        elif context_name:
            outgoing_context = context_name
        else:
            outgoing_context = None

        if outgoing_context:
            options.append(('context', outgoing_context))
        if context_name:
            options.append(('set_var', f'TRANSFER_CONTEXT={context_name}'))

        for user in self._line.users:
            options.append(('set_var', f'XIVO_USERID={user.id}'))  # Deprecated in 24.01
            options.append(('set_var', f'WAZO_USERID={user.id}'))
            options.append(
                ('set_var', f'XIVO_USERUUID={user.uuid}')
            )  # Deprecated in 24.01
            options.append(('set_var', f'WAZO_USERUUID={user.uuid}'))
            if user.enableonlinerec:
                options.append(('set_var', 'WAZO_USER_DTMF_RECORD_TOGGLE_ENABLED=1'))
            options.append(('set_var', f'WAZO_CALLER_SIMULTCALLS={user.simultcalls}'))

        if self._line.extensions:
            for extension in self._line.extensions:
                options.append(
                    ('set_var', f'PICKUPMARK={extension.exten}%{extension.context}')
                )
                break

        options = self._add_mixmonitor_options(
            self._tenants_settings[self._endpoint_config.tenant_uuid], options
        )

        pickup_groups = self._pickup_members.get(self._endpoint_config.uuid, {})
        named_pickup_groups = ','.join(
            str(id) for id in pickup_groups.get('pickupgroup', [])
        )
        if named_pickup_groups:
            options.append(('named_pickup_group', named_pickup_groups))

        named_call_groups = ','.join(
            str(id) for id in pickup_groups.get('callgroup', [])
        )
        if named_call_groups:
            options.append(('named_call_group', named_call_groups))

        options = self._add_mailboxes(options)

        return options


def merge_endpoints_and_template(items, Klass, endpoint_field, *args):
    resolved_configs = {}

    def add_endpoint_configuration(endpoint, item=None):
        for parent in endpoint.templates:
            if parent.uuid in resolved_configs:
                continue
            add_endpoint_configuration(parent)

        if item:
            endpoint_config = Klass(item, resolved_configs, *args)
        else:
            endpoint_config = _SIPEndpointResolver(endpoint, resolved_configs)

        resolved_configs[endpoint.uuid] = endpoint_config

    for item in items:
        add_endpoint_configuration(getattr(item, endpoint_field), item)

    endpoint_configs = (
        endpoint_config
        for endpoint_config in resolved_configs.values()
        if not endpoint_config.template
    )
    return [endpoint_config.resolve() for endpoint_config in endpoint_configs]


@daosession
def find_sip_meeting_guests_settings(session):
    tenant_settings = find_tenant_settings()
    query = (
        session.query(
            Meeting,
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip)
            .joinedload(EndpointSIP.template_relations)
            .joinedload(EndpointSIPTemplate.parent),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(EndpointSIP._aor_section),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._auth_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._endpoint_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._registration_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._registration_outbound_auth_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._identify_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(
                EndpointSIP._outbound_auth_section
            ),
        )
        .options(
            joinedload(Meeting.guest_endpoint_sip).joinedload(EndpointSIP.transport),
        )
        .filter(Meeting.guest_endpoint_sip_uuid.isnot(None))
    )

    return merge_endpoints_and_template(
        query.all(), _EndpointSIPMeetingResolver, 'guest_endpoint_sip', tenant_settings
    )


@daosession
def find_sip_user_settings(session):
    pickup_members = find_pickup_members('sip')
    tenant_settings = find_tenant_settings()
    query = (
        session.query(
            LineFeatures,
        )
        .options(
            joinedload(LineFeatures.endpoint_sip)
            .joinedload(EndpointSIP.template_relations)
            .joinedload(EndpointSIPTemplate.parent),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(EndpointSIP._aor_section),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(EndpointSIP._auth_section),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(
                EndpointSIP._endpoint_section
            ),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(
                EndpointSIP._registration_section
            ),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(
                EndpointSIP._registration_outbound_auth_section
            ),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(
                EndpointSIP._identify_section
            ),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(
                EndpointSIP._outbound_auth_section
            ),
        )
        .options(
            joinedload(LineFeatures.endpoint_sip).joinedload(EndpointSIP.transport),
        )
        .options(
            joinedload(LineFeatures.user_lines)
            .joinedload(UserLine.user)
            .joinedload(UserFeatures.voicemail),
        )
        .options(
            joinedload(LineFeatures.line_extensions).joinedload(
                LineExtension.extension
            ),
        )
        .filter(
            LineFeatures.endpoint_sip_uuid.isnot(None),
        )
    )

    return merge_endpoints_and_template(
        query.all(),
        _EndpointSIPLineResolver,
        'endpoint_sip',
        pickup_members,
        tenant_settings,
    )


@daosession
def find_sip_trunk_settings(session):
    tenant_settings = find_tenant_settings()
    query = (
        session.query(
            TrunkFeatures,
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip)
            .joinedload(EndpointSIP.template_relations)
            .joinedload(EndpointSIPTemplate.parent),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(EndpointSIP._aor_section),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._auth_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._endpoint_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._registration_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._registration_outbound_auth_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._identify_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(
                EndpointSIP._outbound_auth_section
            ),
        )
        .options(
            joinedload(TrunkFeatures.endpoint_sip).joinedload(EndpointSIP.transport),
        )
        .filter(
            TrunkFeatures.endpoint_sip_uuid.isnot(None),
        )
    )

    return merge_endpoints_and_template(
        query.all(), _EndpointSIPTrunkResolver, 'endpoint_sip', tenant_settings
    )


@daosession
def find_tenant_settings(session):
    res = dict()
    rows = session.query(Tenant).all()
    for row in rows:
        row_dict = row.todict()
        res[row_dict['uuid']] = row_dict
    return res


@daosession
def find_pickup_members(session, protocol):
    '''
    Returns a map:
    {endpoint_id: {pickupgroup: set([pickupgroup_id, ...]),
                   callgroup: set([pickupgroup_id, ...])},
     ...,
    }
    '''
    group_map = {
        'member': 'pickupgroup',
        'pickup': 'callgroup',
    }

    res = defaultdict(lambda: defaultdict(set))

    def _add_member(m):
        if protocol == 'sip':
            res_base = res[m.endpoint_sip_uuid]
        elif protocol == 'sccp':
            res_base = res[m.endpoint_sccp_id]
        elif protocol == 'custom':
            res_base = res[m.endpoint_custom_id]
        return res_base[group_map[m.category]].add(m.id)

    add_member = _add_member

    base_query = (
        session.query(
            PickupMember.category,
            Pickup.id,
            LineFeatures.endpoint_sip_uuid,
            LineFeatures.endpoint_sccp_id,
            LineFeatures.endpoint_custom_id,
        )
        .join(
            Pickup,
            Pickup.id == PickupMember.pickupid,
        )
        .filter(Pickup.commented == 0)
    )

    if protocol == 'sip':
        base_query = base_query.filter(LineFeatures.endpoint_sip_uuid.isnot(None))
    elif protocol == 'sccp':
        base_query = base_query.filter(LineFeatures.endpoint_sccp_id.isnot(None))
    elif protocol == 'custom':
        base_query = base_query.filter(LineFeatures.endpoint_custom_id.isnot(None))

    users = (
        base_query.join(
            UserLine,
            UserLine.user_id == PickupMember.memberid,
        )
        .join(
            LineFeatures,
            LineFeatures.id == UserLine.line_id,
        )
        .filter(
            PickupMember.membertype == 'user',
        )
    )

    groups = (
        base_query.join(
            GroupFeatures,
            GroupFeatures.id == PickupMember.memberid,
        )
        .join(
            QueueMember,
            QueueMember.queue_name == GroupFeatures.name,
        )
        .join(
            UserLine,
            UserLine.user_id == QueueMember.userid,
        )
        .join(
            LineFeatures,
            LineFeatures.id == UserLine.line_id,
        )
        .filter(
            and_(
                PickupMember.membertype == 'group',
                QueueMember.usertype == 'user',
                UserLine.main_user == True,  # noqa
                UserLine.main_line == True,  # noqa
            )
        )
    )

    queues = (
        base_query.join(
            QueueFeatures,
            QueueFeatures.id == PickupMember.memberid,
        )
        .join(
            QueueMember,
            QueueMember.queue_name == QueueFeatures.name,
        )
        .join(
            UserLine,
            UserLine.user_id == QueueMember.userid,
        )
        .join(
            LineFeatures,
            LineFeatures.id == UserLine.line_id,
        )
        .filter(
            and_(
                PickupMember.membertype == 'queue',
                QueueMember.usertype == 'user',
                UserLine.main_user == True,  # noqa
                UserLine.main_line == True,  # noqa
            )
        )
    )

    for member in users.union(groups.union(queues)).all():
        add_member(member)

    return res


@daosession
def find_iax_general_settings(session):
    rows = session.query(StaticIAX).filter(StaticIAX.commented == 0).all()

    res = []
    for row in rows:
        res.append(
            {
                'var_name': row.var_name,
                'var_val': row.var_val,
            }
        )

    return res


@daosession
def find_iax_trunk_settings(session):
    rows = (
        session.query(UserIAX)
        .filter(
            and_(
                UserIAX.commented == 0,
                UserIAX.category == 'trunk',
            )
        )
        .all()
    )

    return rows


@daosession
def find_iax_calllimits_settings(session):
    rows = session.query(IAXCallNumberLimits).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_general_settings(session):
    rows = (
        session.query(StaticQueue)
        .filter(
            and_(
                StaticQueue.commented == 0,
                StaticQueue.category == 'general',
            )
        )
        .all()
    )

    return [row.todict() for row in rows]


@daosession
def find_queue_settings(session):
    rows = (
        session.query(Queue)
        .options(joinedload(Queue.groupfeatures))
        .options(joinedload(Queue.queuefeatures))
        .filter(Queue.commented == 0)
        .all()
    )

    result = []
    for row in rows:
        row_as_dict = row.todict()
        row_as_dict['label'] = row.label
        result.append(row_as_dict)
    return result


@daosession
def find_queue_skillrule_settings(session):
    rows = session.query(QueueSkillRule).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_members_settings(session, queue_name):
    user_members = (
        session.query(
            QueueMember.category,
            QueueMember.penalty,
            QueueMember.position,
            QueueMember.interface,
            UserFeatures.uuid,
        )
        .outerjoin(UserFeatures, QueueMember.userid == UserFeatures.id)
        .filter(
            and_(
                QueueMember.commented == 0,
                QueueMember.queue_name == queue_name,
                QueueMember.usertype == 'user',
            )
        )
        .order_by(QueueMember.position)
        .all()
    )

    def is_user(row):
        return row.uuid is not None

    res = []
    for row in user_members:
        if is_user(row):
            member = Member(
                interface=f'Local/{row.uuid}@usersharedlines',
                penalty=str(row.penalty),
                name='',
                state_interface=f'hint:{row.uuid}@usersharedlines',
            )
        else:
            member = Member(
                interface=row.interface,
                penalty=str(row.penalty),
                name='',
                state_interface='',
            )
        res.append(member)
    return res


@daosession
def find_agent_queue_skills_settings(session):
    rows = (
        session.query(
            AgentFeatures.id,
            QueueSkill.name,
            AgentQueueSkill.weight,
        )
        .filter(
            and_(
                AgentQueueSkill.agentid == AgentFeatures.id,
                AgentQueueSkill.skillid == QueueSkill.id,
            )
        )
        .order_by(AgentFeatures.id)
        .all()
    )

    res = []
    for id_, name, weight in rows:
        res.append(
            {
                'id': id_,
                'name': name,
                'weight': weight,
            }
        )

    return res
