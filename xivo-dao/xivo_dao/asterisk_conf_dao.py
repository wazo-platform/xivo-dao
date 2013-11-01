# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from sqlalchemy.sql.expression import and_, literal, cast
from sqlalchemy.types import VARCHAR

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.linefeatures import LineFeatures
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
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
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


@daosession
def find_sccp_general_settings(session):
    rows = session.query(SCCPGeneralSettings).all()

    row2 = session.query(literal('vmexten').label('option_name'),
                         Extension.exten.label('option_value')).filter(
                    and_(Extension.type == 'extenfeatures',
                         Extension.typeval == 'vmusermsg')).first()

    res = []
    for row in rows:
        tmp = {}
        tmp['option_name'] = row.option_name
        tmp['option_value'] = row.option_value
        res.append(tmp)

    res.append({'option_name': row2.option_name, 'option_value': row2.option_value})

    return res


@daosession
def find_sccp_line_settings(session):
    rows = (session.query(SCCPLine,
                          UserFeatures.language,
                          UserLine.user_id,
                          LineFeatures.context,
                          LineFeatures.number)
            .filter(and_(UserLine.user_id == UserFeatures.id,
                         UserLine.line_id == LineFeatures.id,
                         UserLine.main_user == True,
                         UserLine.main_line == True,
                         LineFeatures.protocol == 'sccp',
                         LineFeatures.protocolid == SCCPLine.id))
            .all())

    res = []
    for row in rows:
        sccpline, language, user_id, context, number = row
        tmp = {}
        tmp['name'] = sccpline.name
        tmp['cid_name'] = sccpline.cid_name
        tmp['cid_num'] = sccpline.cid_num
        tmp['user_id'] = user_id
        tmp['number'] = number
        tmp['context'] = context
        tmp['language'] = language
        res.append(tmp)

    return res


@daosession
def find_sccp_device_settings(session):
    rows = session.query(SCCPDevice).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_sccp_speeddial_settings(session):
    rows = (session.query(PhoneFunckey,
                         UserLine.user_id,
                         SCCPDevice.device)
            .filter(and_(UserLine.user_id == PhoneFunckey.iduserfeatures,
                         UserLine.line_id == LineFeatures.id,
                         UserLine.main_user == True,
                         LineFeatures.protocol == 'sccp',
                         LineFeatures.number == SCCPDevice.line))
            .all())

    res = []
    for row in rows:
        phonefunckey, user_id, device = row
        tmp = {}
        tmp['exten'] = phonefunckey.exten
        tmp['fknum'] = phonefunckey.fknum
        tmp['label'] = phonefunckey.label
        tmp['supervision'] = phonefunckey.supervision
        tmp['user_id'] = user_id
        tmp['device'] = device
        res.append(tmp)

    return res


@daosession
def find_featuremap_features_settings(session):
    rows = session.query(Features).filter(and_(Features.commented == 0, Features.category == 'featuremap')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_general_features_settings(session):
    rows = session.query(Features).filter(and_(Features.commented == 0, Features.category == 'general')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_exten_progfunckeys_settings(session, context_name):
    rows = (session.query(PhoneFunckey.iduserfeatures,
                          PhoneFunckey.exten,
                          PhoneFunckey.typeextenumbers,
                          PhoneFunckey.typevalextenumbers,
                          PhoneFunckey.typeextenumbersright,
                          PhoneFunckey.typevalextenumbersright,
                          Extension.exten.label('leftexten'))
            .filter(and_(UserLine.user_id == PhoneFunckey.iduserfeatures,
                         UserLine.line_id == LineFeatures.id,
                         UserLine.main_user == True,
                         UserLine.main_line == True,
                         LineFeatures.context == context_name,
                         PhoneFunckey.typeextenumbers != None,
                         PhoneFunckey.typevalextenumbers != None,
                         PhoneFunckey.typevalextenumbers != 'user',
                         cast(PhoneFunckey.typeextenumbers, VARCHAR) == cast(Extension.type, VARCHAR),
                         PhoneFunckey.supervision == 1,
                         PhoneFunckey.progfunckey == 1))
            .all())

    res = []
    for row in rows:
        user_id, exten, typeextenumbers, typevalextenumbers, typeextenumbersright, typevalextenumbersright, leftexten = row
        tmp = {}
        tmp['user_id'] = user_id
        tmp['exten'] = exten
        tmp['typeextenumbers'] = typeextenumbers
        tmp['typevalextenumbers'] = typevalextenumbers
        tmp['typeextenumbersright'] = typeextenumbersright
        tmp['typevalextenumbersright'] = typevalextenumbersright
        tmp['leftexten'] = leftexten
        res.append(tmp)

    return res


@daosession
def find_exten_phonefunckeys_settings(session, context_name):
    """get all supervised user/group/queue/meetme
    """
    rows = (session.query(PhoneFunckey.typeextenumbersright,
                          PhoneFunckey.typevalextenumbersright,
                          Extension.exten)
            .outerjoin(Extension, and_(cast(PhoneFunckey.typeextenumbersright, VARCHAR) == cast(Extension.type, VARCHAR),
                                       PhoneFunckey.typevalextenumbersright == Extension.typeval))
            .filter(and_(UserLine.user_id == PhoneFunckey.iduserfeatures,
                         UserLine.line_id == LineFeatures.id,
                         UserLine.main_user == True,
                         UserLine.main_line == True,
                         LineFeatures.context == context_name,
                         PhoneFunckey.typeextenumbers == None,
                         PhoneFunckey.typevalextenumbers == None,
                         PhoneFunckey.typeextenumbersright.in_(('group', 'queue', 'meetme')),
                         PhoneFunckey.supervision == 1))
            .all())

    res = []
    for row in rows:
        typeextenumbersright, typevalextenumbersright, exten = row
        tmp = {}
        tmp['typeextenumbersright'] = typeextenumbersright
        tmp['typevalextenumbersright'] = typevalextenumbersright
        tmp['exten'] = exten
        res.append(tmp)

    return res


@daosession
def find_exten_xivofeatures_setting(session):
    rows = session.query(Extension).filter(
            and_(Extension.context == 'xivo-features',
                 Extension.commented == 0)).order_by('exten').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_extenfeatures_settings(session, features=[]):
    rows = session.query(Extension).filter(
            and_(Extension.context == 'xivo-features',
                 Extension.type == 'extenfeatures',
                 Extension.typeval.in_(features))).order_by('exten').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_exten_settings(session, context_name):
    rows = session.query(Extension).filter(
                        and_(Extension.context == context_name,
                             Extension.commented == 0)).order_by('exten').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_exten_hints_settings(session, context_name):
    rows = (session.query(UserFeatures.id,
                          UserFeatures.enablevoicemail,
                          LineFeatures.number,
                          LineFeatures.name,
                          LineFeatures.protocol,
                          Voicemail.uniqueid)
            .outerjoin(Voicemail, UserFeatures.voicemailid == Voicemail.uniqueid)
            .filter(and_(UserLine.user_id == UserFeatures.id,
                         UserLine.line_id == LineFeatures.id,
                         UserLine.main_user == True,
                         UserLine.main_line == True,
                         LineFeatures.context == context_name,
                         UserFeatures.enablehint == 1))
            .all())

    res = []
    for row in rows:
        user_id, enablevoicemail, number, name, protocol, voicemail_id = row
        tmp = {}
        tmp['user_id'] = user_id
        tmp['enablevoicemail'] = enablevoicemail
        tmp['number'] = number
        tmp['name'] = name
        tmp['protocol'] = protocol
        tmp['voicemail_id'] = voicemail_id
        res.append(tmp)

    return res


@daosession
def find_context_settings(session):
    rows = session.query(Context).filter(Context.commented == 0).order_by('name').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_contextincludes_settings(session, context_name):
    rows = session.query(ContextInclude).filter(ContextInclude.context == context_name).order_by('priority').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_voicemail_activated(session):
    rows = session.query(Voicemail).filter(Voicemail.commented == 0).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


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

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_sip_trunk_settings(session):
    rows = session.query(UserSIP).filter(and_(UserSIP.category == 'trunk',
                                              UserSIP.commented == 0)).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_sip_user_settings(session):
    rows = session.query(UserSIP,
                         LineFeatures.number).filter(
            and_(UserSIP.category == 'user',
                 UserSIP.commented == 0,
                 LineFeatures.protocol == 'sip',
                 LineFeatures.protocolid == UserSIP.id)).all()

    res = []
    for row in rows:
        user_sip, number = row
        tmp = user_sip.todict()
        tmp['number'] = number
        res.append(tmp)

    return res


@daosession
def find_sip_pickup_settings(session):
    # simple users
    q1 = (session.query(UserSIP.name,
                        PickupMember.category,
                        Pickup.id)
          .filter(and_(Pickup.commented == 0,
                       Pickup.id == PickupMember.pickupid,
                       PickupMember.membertype == 'user',
                       PickupMember.memberid == UserLine.user_id,
                       LineFeatures.id == UserLine.line_id,
                       LineFeatures.protocol == 'sip',
                       LineFeatures.protocolid == UserSIP.id))
          )

    # groups
    q2 = (session.query(UserSIP.name,
                        PickupMember.category,
                        Pickup.id)
          .filter(and_(Pickup.commented == 0,
                       Pickup.id == PickupMember.pickupid,
                       PickupMember.membertype == 'group',
                       PickupMember.memberid == GroupFeatures.id,
                       GroupFeatures.name == QueueMember.queue_name,
                       QueueMember.usertype == 'user',
                       QueueMember.userid == UserLine.user_id,
                       LineFeatures.id == UserLine.line_id,
                       LineFeatures.protocol == 'sip',
                       LineFeatures.protocolid == UserSIP.id))
          )

    # queues
    q3 = (session.query(UserSIP.name,
                        PickupMember.category,
                        Pickup.id)
          .filter(and_(Pickup.commented == 0,
                       Pickup.id == PickupMember.pickupid,
                       PickupMember.membertype == 'queue',
                       PickupMember.memberid == QueueFeatures.id,
                       QueueFeatures.name == QueueMember.queue_name,
                       QueueMember.usertype == 'user',
                       QueueMember.userid == UserLine.user_id,
                       LineFeatures.id == UserLine.line_id,
                       LineFeatures.protocol == 'sip',
                       LineFeatures.protocolid == UserSIP.id))
        )

    return q1.union(q2.union(q3)).all()


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
def find_iax_calllimits_settings(session):
    rows = session.query(IAXCallNumberLimits).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_iax_trunk_settings(session):
    rows = session.query(StaticIAX).filter(and_(StaticIAX.commented == 0,
                                                StaticIAX.category == 'trunk')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_iax_user_settings(session):
    rows = session.query(StaticIAX).filter(and_(StaticIAX.commented == 0,
                                                StaticIAX.category == 'user')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_meetme_general_settings(session):
    rows = session.query(StaticMeetme).filter(and_(StaticMeetme.commented == 0,
                                                   StaticMeetme.category == 'general')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_meetme_rooms_settings(session):
    rows = session.query(StaticMeetme).filter(and_(StaticMeetme.commented == 0,
                                                   StaticMeetme.category == 'rooms')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_musiconhold_settings(session):
    rows = session.query(MusicOnHold).filter(MusicOnHold.commented == 0).order_by('category').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_queue_general_settings(session):
    rows = session.query(StaticQueue).filter(and_(StaticQueue.commented == 0,
                                                  StaticQueue.category == 'general')).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_queue_settings(session):
    rows = session.query(Queue).filter(Queue.commented == 0).order_by('name').all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_queue_skillrule_settings(session):
    rows = session.query(QueueSkillRule).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_queue_penalty_settings(session):
    rows = session.query(QueuePenalty).filter(QueuePenalty.commented == 0).all()

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_queue_members_settings(session, queue_name):
    rows = (session.query(QueueMember)
            .filter(and_(QueueMember.commented == 0,
                         QueueMember.queue_name == queue_name,
                         QueueMember.usertype == 'user'))
            .order_by(QueueMember.position)
            .all())

    res = []
    for row in rows:
        res.append(row.todict())

    return res


@daosession
def find_agent_queue_skills_settings(session):
    rows = (session.query(AgentFeatures.id, QueueSkill.name, AgentQueueSkill.weight)
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
