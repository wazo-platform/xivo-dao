# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from collections import defaultdict

from sqlalchemy.sql.expression import and_, or_, literal, cast
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.sipauthentication import SIPAuthentication
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
from xivo_dao.alchemy.musiconhold import MusicOnHold
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


@daosession
def find_sccp_general_settings(session):
    rows = session.query(SCCPGeneralSettings).all()

    voicemail_consult_exten = (session.query(literal('vmexten').label('option_name'),
                                             Extension.exten.label('option_value'))
                               .filter(and_(Extension.type == 'extenfeatures',
                                            Extension.typeval == 'vmusermsg'))
                               .first())

    res = []
    for row in rows:
        tmp = {}
        tmp['option_name'] = row.option_name
        tmp['option_value'] = row.option_value
        res.append(tmp)

    res.append(
        {
            'option_name': voicemail_consult_exten.option_name,
            'option_value': voicemail_consult_exten.option_value
        }
    )

    return res


@daosession
def find_sccp_line_settings(session):
    sccp_pickup_members = find_pickup_members('sccp')

    def line_config(protocolid, name, cid_name, cid_num, allow, disallow,
                    language, user_id, context, number):
        line = {
            'name': name,
            'cid_name': cid_name,
            'cid_num': cid_num,
            'user_id': user_id,
            'number': number,
            'context': context,
            'language': language,
        }

        if allow:
            line['allow'] = allow
        if disallow:
            line['disallow'] = disallow

        line.update(sccp_pickup_members.get(protocolid, {}))

        return line

    rows = (session.query(SCCPLine.id,
                          SCCPLine.name,
                          SCCPLine.cid_name,
                          SCCPLine.cid_num,
                          SCCPLine.allow,
                          SCCPLine.disallow,
                          UserFeatures.language,
                          UserLine.user_id,
                          LineFeatures.context,
                          LineFeatures.number)
            .join(LineFeatures, and_(LineFeatures.protocolid == SCCPLine.id,
                                     LineFeatures.protocol == 'sccp'))
            .join(UserLine, and_(UserLine.line_id == LineFeatures.id,
                                 UserLine.main_line == True))
            .join(UserFeatures, and_(UserFeatures.id == UserLine.user_id,
                                     UserLine.main_user == True))
            .filter(LineFeatures.commented == 0)
            .all())

    for row in rows:
        yield line_config(*row)


@daosession
def find_sccp_device_settings(session):
    rows = session.query(SCCPDevice).all()

    return [row.todict() for row in rows]


@daosession
def find_sccp_speeddial_settings(session):
    query = (session.query(FuncKeyMapping.position.label('fknum'),
                           FuncKeyMapping.label.label('label'),
                           cast(FuncKeyMapping.blf, Integer).label('supervision'),
                           FuncKeyDestCustom.exten.label('exten'),
                           UserFeatures.id.label('user_id'),
                           SCCPDevice.device.label('device'))
             .join(UserFeatures,
                   FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id)
             .join(FuncKeyDestCustom,
                   FuncKeyDestCustom.func_key_id == FuncKeyMapping.func_key_id)
             .join(UserLine,
                   and_(
                       UserLine.user_id == UserFeatures.id,
                       UserLine.main_user == True))
             .join(LineFeatures,
                   UserLine.line_id == LineFeatures.id)
             .join(SCCPLine,
                   and_(
                       LineFeatures.protocol == 'sccp',
                       LineFeatures.protocolid == SCCPLine.id))
             .join(SCCPDevice,
                   SCCPLine.name == SCCPDevice.line)
             .filter(LineFeatures.commented == 0)
             )

    keys = [{'exten': row.exten,
            'fknum': row.fknum,
            'label': row.label,
            'supervision': row.supervision,
            'user_id': row.user_id,
            'device': row.device}
            for row in query]

    return keys


@daosession
def find_featuremap_features_settings(session):
    rows = session.query(Features).filter(and_(Features.commented == 0, Features.category == 'featuremap')).all()

    return [row.todict() for row in rows]


@daosession
def find_general_features_settings(session):
    rows = session.query(Features).filter(and_(Features.commented == 0, Features.category == 'general')).all()

    return [row.todict() for row in rows]


@daosession
def find_exten_conferences_settings(session, context_name):
    rows = (session.query(MeetmeFeatures.confno)
            .filter(MeetmeFeatures.context == context_name))
    return [{'exten': row[0]} for row in rows]


@daosession
def find_exten_xivofeatures_setting(session):
    rows = (session.query(Extension)
            .filter(and_(Extension.context == 'xivo-features',
                         Extension.commented == 0)).order_by('exten')
            .all())

    return [row.todict() for row in rows]


@daosession
def find_extenfeatures_settings(session, features=None):
    features = features or []

    query = (session.query(Extension)
             .filter(and_(Extension.context == 'xivo-features',
                          Extension.type == 'extenfeatures'))
             .order_by('exten'))

    if features:
        query = query.filter(Extension.typeval.in_(features))

    return [row.todict() for row in query.all()]


@daosession
def find_exten_settings(session, context_name):
    rows = (session.query(Extension)
            .outerjoin(UserLine, and_(UserLine.extension_id == Extension.id,
                                      UserLine.main_user == True,
                                      UserLine.main_line == True))
            .outerjoin(LineFeatures, LineFeatures.id == UserLine.line_id)
            .filter(and_(Extension.context == context_name,
                         Extension.commented == 0,
                         or_(UserLine.line_id == None,
                             LineFeatures.commented == 0)))
            .order_by('exten')
            .all())

    return [row.todict() for row in rows]


@daosession
def find_context_settings(session):
    rows = session.query(Context).filter(Context.commented == 0).order_by('name').all()

    return [row.todict() for row in rows]


@daosession
def find_contextincludes_settings(session, context_name):
    rows = session.query(ContextInclude).filter(ContextInclude.context == context_name).order_by('priority').all()

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
        tmp = {}
        tmp['category'] = row.category
        tmp['var_name'] = row.var_name
        tmp['var_val'] = row.var_val
        res.append(tmp)

    return res


@daosession
def find_sip_general_settings(session):
    rows = session.query(StaticSIP).filter(StaticSIP.commented == 0).all()

    res = []
    for row in rows:
        tmp = {}
        tmp['var_name'] = row.var_name
        tmp['var_val'] = row.var_val
        res.append(tmp)

    return res


@daosession
def find_sip_authentication_settings(session):
    rows = session.query(SIPAuthentication).all()

    return [row.todict() for row in rows]


@daosession
def find_sip_trunk_settings(session):
    rows = session.query(UserSIP).filter(and_(UserSIP.category == 'trunk',
                                              UserSIP.commented == 0)).all()

    return [row.todict() for row in rows]


@daosession
def find_sip_user_settings(session):
    def gen_user(user_sip, number, moh):
        user_config = user_sip.todict()
        user_config['number'] = number
        user_config['mohsuggest'] = moh
        return user_config

    rows = (
        session.query(
            UserSIP,
            LineFeatures.number,
            UserFeatures.musiconhold,
        ).join(
            LineFeatures, and_(LineFeatures.protocolid == UserSIP.id,
                               LineFeatures.protocol == 'sip')
        ).outerjoin(
            UserLine, UserLine.line_id == LineFeatures.id
        ).outerjoin(
            UserFeatures, UserFeatures.id == UserLine.user_id
        ).filter(
            and_(
                UserSIP.category == 'user',
                UserSIP.commented == 0,
            )
        ).all()
    )

    return (gen_user(*row) for row in rows)


@daosession
def find_pickup_members(session, protocol):
    '''
    Returns a map:
    {protocolid: {pickupgroup: set([pickupgroup_id, ...]),
                  callgroup: set([pickupgroup_id, ...])},
     ...,
    }
    '''
    group_map = {'member': 'pickupgroup',
                 'pickup': 'callgroup'}

    res = defaultdict(lambda: defaultdict(set))
    add_member = lambda m: res[m.protocolid][group_map[m.category]].add(m.id)

    base_query = session.query(
        PickupMember.category,
        Pickup.id,
        LineFeatures.protocol,
        LineFeatures.protocolid,
    ).join(
        Pickup, Pickup.id == PickupMember.pickupid,
    ).filter(
        and_(
            Pickup.commented == 0,
            LineFeatures.protocol == protocol,
        )
    )

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
            UserLine.main_user == True,
            UserLine.main_line == True,
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
            UserLine.main_user == True,
            UserLine.main_line == True,
        )
    )

    for member in users.union(groups.union(queues)).all():
        add_member(member)

    return res


@daosession
def find_sip_pickup_settings(session):
    pickup_members = find_pickup_members('sip')

    if not pickup_members:
        return

    sip_users = session.query(
        UserSIP.id,
        UserSIP.name,
    ).filter(UserSIP.id.in_(pickup_members.keys()))

    for sip_user in sip_users.all():
        pickup_entry = pickup_members[sip_user.id]

        for pickup_id in pickup_entry.get('pickupgroup', []):
            yield sip_user.name, 'member', pickup_id

        for pickup_id in pickup_entry.get('callgroup', []):
            yield sip_user.name, 'pickup', pickup_id


@daosession
def find_iax_general_settings(session):
    rows = session.query(StaticIAX).filter(StaticIAX.commented == 0).all()

    res = []
    for row in rows:
        tmp = {}
        tmp['var_name'] = row.var_name
        tmp['var_val'] = row.var_val
        res.append(tmp)

    return res


@daosession
def find_iax_trunk_settings(session):
    rows = session.query(UserIAX).filter(and_(UserIAX.commented == 0,
                                              UserIAX.category == 'trunk')).all()

    return [row.todict() for row in rows]


@daosession
def find_iax_calllimits_settings(session):
    rows = session.query(IAXCallNumberLimits).all()

    return [row.todict() for row in rows]


@daosession
def find_meetme_general_settings(session):
    rows = session.query(StaticMeetme).filter(and_(StaticMeetme.commented == 0,
                                                   StaticMeetme.category == 'general')).all()

    return [row.todict() for row in rows]


@daosession
def find_meetme_rooms_settings(session):
    rows = session.query(StaticMeetme).filter(and_(StaticMeetme.commented == 0,
                                                   StaticMeetme.category == 'rooms')).all()

    return [row.todict() for row in rows]


@daosession
def find_musiconhold_settings(session):
    rows = session.query(MusicOnHold).filter(MusicOnHold.commented == 0).order_by('category').all()

    return [row.todict() for row in rows]


@daosession
def find_queue_general_settings(session):
    rows = session.query(StaticQueue).filter(and_(StaticQueue.commented == 0,
                                                  StaticQueue.category == 'general')).all()

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
    rows = (session.query(QueueMember.penalty,
                          QueueMember.interface)
            .filter(and_(QueueMember.commented == 0,
                         QueueMember.queue_name == queue_name,
                         QueueMember.usertype == 'user'))
            .order_by(QueueMember.position)
            .all())

    res = []
    for row in rows:
        penalty, interface = row
        tmp = {}
        tmp['penalty'] = penalty
        tmp['interface'] = interface
        res.append(tmp)

    return res


@daosession
def find_agent_queue_skills_settings(session):
    rows = (session.query(AgentFeatures.id,
                          QueueSkill.name,
                          AgentQueueSkill.weight)
            .filter(and_(AgentQueueSkill.agentid == AgentFeatures.id,
                         AgentQueueSkill.skillid == QueueSkill.id))
            .order_by(AgentFeatures.id)
            .all())

    res = []
    for row in rows:
        agent_id, queueskill_name, agent_queue_skill_weight = row
        tmp = {}
        tmp['id'] = agent_id
        tmp['name'] = queueskill_name
        tmp['weight'] = agent_queue_skill_weight
        res.append(tmp)

    return res


@daosession
def find_queue_penalties_settings(session):
    rows = (session.query(QueuePenalty.name,
                          QueuePenaltyChange)
            .filter(and_(QueuePenalty.id == QueuePenaltyChange.queuepenalty_id,
                         QueuePenalty.commented == 0))
            .order_by(QueuePenalty.name)
            .all())

    res = []
    for row in rows:
        queue_name, queue_penalty_change = row
        tmp = {}
        tmp['name'] = queue_name
        tmp['seconds'] = queue_penalty_change.seconds
        tmp['maxp_sign'] = queue_penalty_change.maxp_sign
        tmp['maxp_value'] = queue_penalty_change.maxp_value
        tmp['minp_sign'] = queue_penalty_change.minp_sign
        tmp['minp_value'] = queue_penalty_change.minp_value
        res.append(tmp)

    return res
