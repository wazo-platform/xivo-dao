# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from collections import (
    defaultdict,
    namedtuple,
)

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import (
    and_,
    cast,
    func,
    literal,
    or_,
)
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuepenalty import QueuePenalty
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.queuepenaltychange import QueuePenaltyChange
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.resources.features.search import PARKING_OPTIONS


@daosession
def find_sccp_general_settings(session):
    rows = session.query(SCCPGeneralSettings).all()

    voicemail_consult_exten = session.query(
        literal('vmexten').label('option_name'),
        Extension.exten.label('option_value'),
    ).filter(and_(
        Extension.type == 'extenfeatures',
        Extension.typeval == 'vmusermsg',
    )).first()

    res = [{
        'option_name': row.option_name,
        'option_value': row.option_value,
    } for row in rows]

    res.append({
        'option_name': voicemail_consult_exten.option_name,
        'option_value': voicemail_consult_exten.option_value
    })

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
        ) = args

        line = {
            'name': name,
            'cid_name': cid_name,
            'cid_num': cid_num,
            'user_id': user_id,
            'number': number,
            'context': context,
            'language': language,
            'uuid': uuid,
            'tenant_uuid': tenant_uuid,
        }

        if allow:
            line['allow'] = allow
        if disallow:
            line['disallow'] = disallow

        line.update(sccp_pickup_members.get(endpoint_sccp_id, {}))

        return line

    rows = session.query(
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
    ).join(LineFeatures, and_(
        LineFeatures.endpoint_sccp_id == SCCPLine.id,
    )).join(
        UserLine, UserLine.line_id == LineFeatures.id,
    ).join(UserFeatures, and_(
        UserFeatures.id == UserLine.user_id, UserLine.main_user.is_(True),
    )).join(LineExtension, and_(
        LineFeatures.id == LineExtension.line_id,
        LineExtension.main_extension.is_(True),
    )).join(
        Extension, LineExtension.extension_id == Extension.id,
    ).filter(LineFeatures.commented == 0).all()

    for row in rows:
        yield line_config(*row)


@daosession
def find_sccp_device_settings(session):
    query = session.query(
        SCCPDevice,
        Voicemail.mailbox,
    ).outerjoin(
        SCCPLine, SCCPLine.name == SCCPDevice.line,
    ).outerjoin(LineFeatures, and_(
        LineFeatures.endpoint_sccp_id == SCCPLine.id,
    )).outerjoin(UserLine, and_(
        UserLine.line_id == LineFeatures.id,
        UserLine.main_user.is_(True),
    )).outerjoin(
        UserFeatures, UserFeatures.id == UserLine.user_id,
    ).outerjoin(
        Voicemail, Voicemail.uniqueid == UserFeatures.voicemailid,
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
    query = session.query(
        FuncKeyMapping.position.label('fknum'),
        func.translate(FuncKeyMapping.label, invalid_chars, '').label('label'),
        cast(FuncKeyMapping.blf, Integer).label('supervision'),
        func.translate(FuncKeyDestCustom.exten, invalid_chars, '').label('exten'),
        UserFeatures.id.label('user_id'),
        SCCPDevice.device.label('device'),
    ).join(
        UserFeatures,
        FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
    ).join(
        FuncKeyDestCustom,
        FuncKeyDestCustom.func_key_id == FuncKeyMapping.func_key_id,
    ).join(UserLine, and_(
        UserLine.user_id == UserFeatures.id,
        UserLine.main_user.is_(True),
    )).join(
        LineFeatures, UserLine.line_id == LineFeatures.id,
    ).join(SCCPLine, and_(
        LineFeatures.endpoint_sccp_id == SCCPLine.id,
    )).join(
        SCCPDevice, SCCPLine.name == SCCPDevice.line,
    ).filter(LineFeatures.commented == 0)

    return [{
        'exten': row.exten,
        'fknum': row.fknum,
        'label': row.label,
        'supervision': row.supervision,
        'user_id': row.user_id,
        'device': row.device,
    } for row in query]


@daosession
def find_features_settings(session):
    rows = session.query(
        Features.category, Features.var_name, Features.var_val,
    ).filter(and_(
        Features.commented == 0,
        or_(
            and_(
                Features.category == 'general',
                ~Features.var_name.in_(PARKING_OPTIONS)
            ),
            Features.category == 'featuremap',
            Features.category == 'applicationmap',
        )
    )).all()

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
def find_parking_settings(session):
    rows = session.query(
        Features.var_name, Features.var_val,
    ).filter(and_(
        Features.commented == 0,
        Features.category == 'general',
        Features.var_name.in_(PARKING_OPTIONS),
    )).all()

    general_options = []
    default_parking_lot_options = []
    for row in rows:
        option = (row.var_name, row.var_val)
        if row.var_name == 'parkeddynamic':
            general_options.append(option)
        else:
            default_parking_lot_options.append(option)

    return {
        'general_options': general_options,
        'parking_lots': [{
            'name': 'default',
            'options': default_parking_lot_options,
        }],
    }


@daosession
def find_exten_conferences_settings(session, context_name):
    rows = session.query(MeetmeFeatures.confno).filter(MeetmeFeatures.context == context_name)
    return [{'exten': row[0]} for row in rows]


@daosession
def find_exten_xivofeatures_setting(session):
    rows = session.query(Extension).filter(and_(
        Extension.context == 'xivo-features',
        Extension.commented == 0,
    )).order_by('exten').all()

    return [row.todict() for row in rows]


@daosession
def find_extenfeatures_settings(session, features):
    query = session.query(Extension).filter(and_(
        Extension.context == 'xivo-features',
        Extension.type == 'extenfeatures',
        Extension.typeval.in_(features),
    )).order_by('exten')

    return query.all()


@daosession
def find_exten_settings(session, context_name):
    rows = session.query(Extension).outerjoin(
        LineExtension, Extension.id == LineExtension.extension_id,
    ).outerjoin(
        LineFeatures, LineFeatures.id == LineExtension.line_id,
    ).filter(and_(
        Extension.context == context_name,
        Extension.commented == 0,
        Extension.typeval != '0',
        Extension.type != 'parking',
        or_(
            LineExtension.line_id.is_(None),
            LineFeatures.commented == 0,
        ),
    )).order_by('exten').all()

    return [dict(tenant_uuid=row.context_rel.tenant_uuid, **row.todict()) for row in rows]


@daosession
def find_context_settings(session):
    rows = session.query(Context).filter(Context.commented == 0).order_by('name').all()

    return [row.todict() for row in rows]


@daosession
def find_contextincludes_settings(session, context_name):
    rows = session.query(ContextInclude).filter(
        ContextInclude.context == context_name
    ).order_by('priority').all()

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
        res.append({
            'category': row.category,
            'var_name': row.var_name,
            'var_val': row.var_val,
        })

    return res


@daosession
def find_sip_general_settings(session):
    rows = session.query(StaticSIP).filter(StaticSIP.commented == 0).all()

    res = []
    for row in rows:
        res.append({
            'var_name': row.var_name,
            'var_val': row.var_val,
        })

    return res


@daosession
def find_sip_user_settings(session):
    pickup_members = find_pickup_members('sip')
    query = session.query(
        LineFeatures,
    ).options(
        joinedload('endpoint_sip').joinedload('template_relations').joinedload('parent'),
    ).options(
        joinedload('endpoint_sip').joinedload('_aor_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('_endpoint_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('_auth_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('transport'),
    ).options(
        joinedload('user_lines').joinedload('user').joinedload('voicemail'),
    ).options(
        joinedload('line_extensions').joinedload('extension'),
    ).filter(
        LineFeatures.endpoint_sip_uuid.isnot(None),
    )

    lines = query.all()
    context_mapping = {}
    extension_mapping = {}
    voicemail_mapping = defaultdict(list)
    user_mapping = defaultdict(list)
    raw_configs = {}
    for line in lines:
        raw_configs[line.endpoint_sip_uuid] = line.endpoint_sip
        context_mapping[line.endpoint_sip_uuid] = line.context
        if line.extensions:
            extension_mapping[line.endpoint_sip_uuid] = line.extensions[0]
        for user in line.users:
            user_mapping[line.endpoint_sip_uuid].append(user)
            if user.voicemail:
                voicemail_mapping[line.endpoint_sip_uuid].append(user.voicemail)

    def get_flat_config(endpoint):
        if endpoint.uuid in flat_configs:
            return flat_configs[endpoint.uuid]

        parents = [get_flat_config(parent) for parent in endpoint.templates]
        base_config = endpoint_to_dict(endpoint)
        context_name = context_mapping.get(endpoint.uuid)
        if context_name:
            base_config['endpoint_section_options'].append(['context', context_name])
            base_config['endpoint_section_options'].append(
                ['set_var', 'TRANSFER_CONTEXT={}'.format(context_name)],
            )
        if endpoint.transport_uuid:
            base_config['endpoint_section_options'].append(
                ['transport', endpoint.transport.name],
            )
        extension = extension_mapping.get(endpoint.uuid)
        if extension:
            base_config['endpoint_section_options'].append(
                ['set_var', 'PICKUPMARK={}%{}'.format(extension.exten, extension.context)]
            )
        voicemails = voicemail_mapping.get(endpoint.uuid, [])
        mailboxes = []
        for voicemail in voicemails:
            mailboxes.append('{}@{}'.format(voicemail.number, voicemail.context))
        if mailboxes:
            base_config['aor_section_options'].append(
                ['mailboxes', ','.join(mailboxes)]
            )
        for user in user_mapping.get(endpoint.uuid, []):
            base_config['endpoint_section_options'].extend([
                ['set_var', 'XIVO_USERID={}'.format(user.id)],
                ['set_var', 'XIVO_USERUUID={}'.format(user.uuid)],
                # TODO(pc-m): document WAZO_USER_UUID and deprecate the XIVO one
                # ['set_var', 'WAZO_USER_UUID={}'.format(user.uuid)],
            ])
        pickup_groups = pickup_members.get(endpoint.uuid, {})
        named_pickup_groups = ','.join(str(id) for id in pickup_groups.get('pickupgroup', []))
        if named_pickup_groups:
            base_config['endpoint_section_options'].append(
                ['named_pickup_group', named_pickup_groups],
            )
        named_call_groups = ','.join(str(id) for id in pickup_groups.get('callgroup', []))
        if named_call_groups:
            base_config['endpoint_section_options'].append(
                ['named_call_group', named_call_groups],
            )
        builder = {}
        for parent in parents + [base_config]:
            for section in [
                'aor_section_options',
                'auth_section_options',
                'endpoint_section_options',
            ]:
                builder.setdefault(section, [])
                parent_options = parent.get(section, [])
                for option in parent_options:
                    builder[section].append(option)
        for key, value in builder.get('endpoint_section_options', []):
            if key == 'callerid':
                builder['endpoint_section_options'].append(
                    ['set_var', 'XIVO_ORIGINAL_CALLER_ID={}'.format(value)]
                )
                break
        builder['endpoint_section_options'].extend([
            ['set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'],
            ['set_var', 'WAZO_TENANT_UUID={}'.format(endpoint.tenant_uuid)],
        ])
        if builder['endpoint_section_options']:
            builder['endpoint_section_options'].append(['type', 'endpoint'])
        if builder['aor_section_options']:
            builder['aor_section_options'].append(['type', 'aor'])
            builder['endpoint_section_options'].append(['aors', endpoint.name])
        if builder['auth_section_options']:
            builder['auth_section_options'].append(['type', 'auth'])
            builder['endpoint_section_options'].append(['auth', endpoint.name])
        builder.update({
            'uuid': base_config['uuid'],
            'name': base_config['name'],
            'label': base_config['label'],
            'template': base_config['template'],
            'asterisk_id': base_config['asterisk_id'],
        })
        if builder['template']:
            flat_configs[builder['uuid']] = builder
        return builder

    # A flat_config is an endpoint config with all inherited fields merged into a single object
    flat_configs = {}
    for uuid, raw_config in raw_configs.items():
        flat_config = get_flat_config(raw_config)
        flat_configs[uuid] = flat_config

    return [
        remove_duplicated_configurations(config)
        for config in flat_configs.values()
        if config['template'] is False
    ]


@daosession
def find_sip_trunk_settings(session):
    query = session.query(
        TrunkFeatures,
    ).options(
        joinedload('endpoint_sip').joinedload('template_relations').joinedload('parent'),
    ).options(
        joinedload('endpoint_sip').joinedload('_aor_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('_endpoint_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('_auth_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('_identify_section'),
    ).options(
        joinedload('endpoint_sip').joinedload('transport'),
    ).filter(
        TrunkFeatures.endpoint_sip_uuid.isnot(None),
    )

    trunks = query.all()
    context_mapping = {}
    raw_configs = {}
    for trunk in trunks:
        raw_configs[trunk.endpoint_sip_uuid] = trunk.endpoint_sip
        context_mapping[trunk.endpoint_sip_uuid] = trunk.context

    def get_flat_config(endpoint):
        if endpoint.uuid in flat_configs:
            return flat_configs[endpoint.uuid]

        parents = [get_flat_config(parent) for parent in endpoint.templates]
        base_config = endpoint_to_dict(endpoint)
        context_name = context_mapping.get(endpoint.uuid)
        if context_name:
            base_config['endpoint_section_options'].append(['context', context_name])
        if endpoint.transport_uuid:
            base_config['endpoint_section_options'].append(
                ['transport', endpoint.transport.name],
            )
        builder = {}
        for parent in parents + [base_config]:
            for section in [
                'aor_section_options',
                'auth_section_options',
                'endpoint_section_options',
                'identify_section_options',
                'registration_section_options',
                'registration_outbound_auth_section_options',
                'outbound_auth_section_options',
            ]:
                builder.setdefault(section, [])
                parent_options = parent.get(section, [])
                for option in parent_options:
                    builder[section].append(option)
        builder['endpoint_section_options'].extend([
            ['set_var', 'WAZO_TENANT_UUID={}'.format(endpoint.tenant_uuid)],
        ])
        if builder['endpoint_section_options']:
            builder['endpoint_section_options'].append(['type', 'endpoint'])
        if builder['aor_section_options']:
            builder['aor_section_options'].append(['type', 'aor'])
            builder['endpoint_section_options'].append(['aors', endpoint.name])
        if builder['auth_section_options']:
            builder['auth_section_options'].append(['type', 'auth'])
            builder['endpoint_section_options'].append(['auth', endpoint.name])
        if builder['identify_section_options']:
            builder['identify_section_options'].append(['type', 'identify'])
        if builder['registration_section_options']:
            builder['registration_section_options'].append(['type', 'registration'])
        if builder['outbound_auth_section_options']:
            builder['outbound_auth_section_options'].append(['type', 'auth'])
        if builder['registration_outbound_auth_section_options']:
            builder['registration_outbound_auth_section_options'].append(['type', 'auth'])
            builder['registration_section_options'].append(
                ['outbound_auth', 'auth_reg_{}'.format(endpoint.name)]
            )
        builder.update({
            'uuid': base_config['uuid'],
            'name': base_config['name'],
            'label': base_config['label'],
            'template': base_config['template'],
            'asterisk_id': base_config['asterisk_id'],
        })
        if builder['template']:
            flat_configs[builder['uuid']] = builder
        return builder

    # A flat_config is an endpoint config with all inherited fields merged into a single object
    flat_configs = {}
    for uuid, raw_config in raw_configs.items():
        flat_config = get_flat_config(raw_config)
        flat_configs[uuid] = flat_config

    return [
        remove_duplicated_configurations(config)
        for config in flat_configs.values()
        if config['template'] is False
    ]


def remove_duplicated_configurations(config):
    sections = [
        'aor_section_options',
        'auth_section_options',
        'endpoint_section_options',
        'registration_section_options',
        'identify_section_options',
        'registration_outbound_auth_section_options',
        'outbound_auth_section_options',
    ]
    for section in sections:
        reverse_pruned_options = []
        visited_options = set()
        for option in reversed(config.get(section, [])):
            if tuple(option) in visited_options:
                continue
            visited_options.add(tuple(option))
            reverse_pruned_options.append(option)
        config[section] = list(reversed(reverse_pruned_options))
    return config


def endpoint_to_dict(endpoint):
    return {
        'uuid': endpoint.uuid,
        'name': endpoint.name,
        'label': endpoint.label,
        'aor_section_options': endpoint.aor_section_options,
        'auth_section_options': endpoint.auth_section_options,
        'endpoint_section_options': endpoint.endpoint_section_options,
        'registration_section_options': endpoint.registration_section_options,
        'registration_outbound_auth_section_options': endpoint.registration_outbound_auth_section_options,
        'identify_section_options': endpoint.identify_section_options,
        'outbound_auth_section_options': endpoint.outbound_auth_section_options,
        'template': endpoint.template,
        'asterisk_id': endpoint.asterisk_id,
    }


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

    base_query = session.query(
        PickupMember.category,
        Pickup.id,
        LineFeatures.endpoint_sip_uuid,
        LineFeatures.endpoint_sccp_id,
        LineFeatures.endpoint_custom_id,
    ).join(
        Pickup, Pickup.id == PickupMember.pickupid,
    ).filter(Pickup.commented == 0)

    if protocol == 'sip':
        base_query = base_query.filter(LineFeatures.endpoint_sip_uuid.isnot(None))
    elif protocol == 'sccp':
        base_query = base_query.filter(LineFeatures.endpoint_sccp_id.isnot(None))
    elif protocol == 'custom':
        base_query = base_query.filter(LineFeatures.endpoint_custom_id.isnot(None))

    users = base_query.join(
        UserLine, UserLine.user_id == PickupMember.memberid,
    ).join(
        LineFeatures, LineFeatures.id == UserLine.line_id,
    ).filter(
        PickupMember.membertype == 'user',
    )

    groups = base_query.join(
        GroupFeatures, GroupFeatures.id == PickupMember.memberid,
    ).join(
        QueueMember, QueueMember.queue_name == GroupFeatures.name,
    ).join(
        UserLine, UserLine.user_id == QueueMember.userid,
    ).join(
        LineFeatures, LineFeatures.id == UserLine.line_id,
    ).filter(
        and_(
            PickupMember.membertype == 'group',
            QueueMember.usertype == 'user',
            UserLine.main_user == True,  # noqa
            UserLine.main_line == True,  # noqa
        )
    )

    queues = base_query.join(
        QueueFeatures, QueueFeatures.id == PickupMember.memberid,
    ).join(
        QueueMember, QueueMember.queue_name == QueueFeatures.name,
    ).join(
        UserLine, UserLine.user_id == QueueMember.userid,
    ).join(
        LineFeatures, LineFeatures.id == UserLine.line_id,
    ).filter(
        and_(
            PickupMember.membertype == 'queue',
            QueueMember.usertype == 'user',
            UserLine.main_user == True,  # noqa
            UserLine.main_line == True,  # noqa
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
        res.append({
            'var_name': row.var_name,
            'var_val': row.var_val,
        })

    return res


@daosession
def find_iax_trunk_settings(session):
    rows = session.query(UserIAX).filter(and_(
        UserIAX.commented == 0,
        UserIAX.category == 'trunk',
    )).all()

    return rows


@daosession
def find_iax_calllimits_settings(session):
    rows = session.query(IAXCallNumberLimits).all()

    return [row.todict() for row in rows]


@daosession
def find_meetme_general_settings(session):
    rows = session.query(StaticMeetme).filter(and_(
        StaticMeetme.commented == 0,
        StaticMeetme.category == 'general',
    )).all()

    return [row.todict() for row in rows]


@daosession
def find_meetme_rooms_settings(session):
    rows = session.query(StaticMeetme).filter(and_(
        StaticMeetme.commented == 0,
        StaticMeetme.category == 'rooms',
    )).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_general_settings(session):
    rows = session.query(StaticQueue).filter(and_(
        StaticQueue.commented == 0,
        StaticQueue.category == 'general',
    )).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_settings(session):
    rows = session.query(Queue).filter(Queue.commented == 0).order_by('name').all()

    return [row.todict() for row in rows]


@daosession
def find_queue_skillrule_settings(session):
    rows = session.query(QueueSkillRule).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_penalty_settings(session):
    rows = session.query(QueuePenalty).filter(QueuePenalty.commented == 0).all()

    return [row.todict() for row in rows]


@daosession
def find_queue_members_settings(session, queue_name):
    user_members = session.query(
        QueueMember.category,
        QueueMember.penalty,
        QueueMember.position,
        QueueMember.interface,
        UserFeatures.uuid,
    ).outerjoin(
        UserFeatures, QueueMember.userid == UserFeatures.id
    ).filter(and_(
        QueueMember.commented == 0,
        QueueMember.queue_name == queue_name,
        QueueMember.usertype == 'user',
    )).order_by(QueueMember.position).all()

    def is_user_in_group(row):
        return row.category == 'group' and row.uuid is not None

    res = []
    Member = namedtuple('Member', ['interface', 'penalty', 'name', 'state_interface'])
    for row in user_members:
        if is_user_in_group(row):
            member = Member(
                interface='Local/{}@usersharedlines'.format(row.uuid),
                penalty=str(row.penalty),
                name='',
                state_interface='hint:{}@usersharedlines'.format(row.uuid),
            )
        else:
            # TODO clean after pjsip migration
            if row.interface.startswith('SIP/'):
                interface = row.interface.replace('SIP', 'PJSIP')
            else:
                interface = row.interface

            member = Member(
                interface=interface,
                penalty=str(row.penalty),
                name='',
                state_interface='',
            )
        res.append(member)
    return res


@daosession
def find_agent_queue_skills_settings(session):
    rows = session.query(
        AgentFeatures.id,
        QueueSkill.name,
        AgentQueueSkill.weight,
    ).filter(and_(
        AgentQueueSkill.agentid == AgentFeatures.id,
        AgentQueueSkill.skillid == QueueSkill.id,
    )).order_by(AgentFeatures.id).all()

    res = []
    for id_, name, weight in rows:
        res.append({
            'id': id_,
            'name': name,
            'weight': weight,
        })

    return res


@daosession
def find_queue_penalties_settings(session):
    rows = session.query(
        QueuePenalty.name,
        QueuePenaltyChange
    ).filter(and_(
        QueuePenalty.id == QueuePenaltyChange.queuepenalty_id,
        QueuePenalty.commented == 0,
    )).order_by(QueuePenalty.name).all()

    res = []
    for name, penalty_change in rows:
        res.append({
            'name': name,
            'seconds': penalty_change.seconds,
            'maxp_sign': penalty_change.maxp_sign,
            'maxp_value': penalty_change.maxp_value,
            'minp_sign': penalty_change.minp_sign,
            'minp_value': penalty_change.minp_value,
        })

    return res
