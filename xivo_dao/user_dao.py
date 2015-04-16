# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from sqlalchemy import and_
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
# the following import is necessary to laod CtiProfiles' definition:
from xivo_dao.resources.func_key_template import dao as func_key_template_dao


def enable_dnd(user_id):
    update(user_id, {'enablednd': 1})


def disable_dnd(user_id):
    update(user_id, {'enablednd': 0})


def enable_filter(user_id):
    update(user_id, {'incallfilter': 1})


def disable_filter(user_id):
    update(user_id, {'incallfilter': 0})


def enable_unconditional_fwd(user_id, destination):
    update(user_id, {'enableunc': 1, 'destunc': destination})


def disable_unconditional_fwd(user_id, destination):
    update(user_id, {'enableunc': 0, 'destunc': destination})


def enable_rna_fwd(user_id, destination):
    update(user_id, {'enablerna': 1, 'destrna': destination})


def disable_rna_fwd(user_id, destination):
    update(user_id, {'enablerna': 0, 'destrna': destination})


def enable_busy_fwd(user_id, destination):
    update(user_id, {'enablebusy': 1, 'destbusy': destination})


def disable_busy_fwd(user_id, destination):
    update(user_id, {'enablebusy': 0, 'destbusy': destination})


def enable_recording(user_id):
    update(user_id, {'callrecord': 1})


def disable_recording(user_id):
    update(user_id, {'callrecord': 0})


@daosession
def update(session, user_id, user_data_dict):
    with commit_or_abort(session):
        result = session.query(UserFeatures).filter(UserFeatures.id == user_id).update(user_data_dict)
    return result


@daosession
def get(session, user_id):
    result = session.query(UserFeatures).filter(UserFeatures.id == int(user_id)).first()
    if result is None:
        raise LookupError()
    return result


@daosession
def get_user_by_number_context(session, exten, context):
    user = (session.query(UserFeatures)
            .join(ExtensionSchema, and_(ExtensionSchema.context == context,
                                        ExtensionSchema.exten == exten,
                                        ExtensionSchema.commented == 0))
            .join(LineFeatures, and_(LineFeatures.commented == 0))
            .join(UserLine, and_(UserLine.user_id == UserFeatures.id,
                                 UserLine.extension_id == ExtensionSchema.id,
                                 UserLine.line_id == LineFeatures.id,
                                 UserLine.main_line == True,
                                 UserLine.main_line == True))
            .first())

    if not user:
        raise LookupError('No user with number %s in context %s', (exten, context))

    return user


@daosession
def find_by_agent_id(session, agent_id):
    res = session.query(UserFeatures).filter(UserFeatures.agentid == int(agent_id))
    return [user.id for user in res]


def agent_id(user_id):
    try:
        return get(user_id).agentid
    except LookupError:
        return None


def is_agent(user_id):
    try:
        id = agent_id(user_id)
        return id is not None
    except LookupError:
        return False


def get_profile(user_id):
    return get(user_id).cti_profile_id


@daosession
def _get_included_contexts(session, context):
    return [line.include for line in (session.query(ContextInclude.include)
                                      .filter(ContextInclude.context == context))]


def _get_nested_contexts(contexts):
    checked = []
    to_check = set(contexts) - set(checked)
    while to_check:
        context = to_check.pop()
        contexts.extend(_get_included_contexts(context))
        checked.append(context)
        to_check = set(contexts) - set(checked)

    return list(set(contexts))


@daosession
def get_reachable_contexts(session, user_id):
    res = (session.query(ExtensionSchema.context)
           .join(UserLine, and_(UserLine.extension_id == ExtensionSchema.id,
                                UserLine.user_id == int(user_id)))
           .join(LineFeatures, UserLine.line_id == LineFeatures.id)
           .all())
    line_contexts = [context[0] for context in res]

    return _get_nested_contexts(line_contexts)


@daosession
def get_agent_number(session, user_id):
    row = (session
           .query(AgentFeatures.number, UserFeatures.agentid)
           .filter(and_(UserFeatures.id == user_id,
                        AgentFeatures.id == UserFeatures.agentid))
           .first())
    if not row:
        raise LookupError('Could not find a agent number for user %s', user_id)
    return row.number


@daosession
def get_dest_unc(session, user_id):
    return session.query(UserFeatures.destunc).filter(UserFeatures.id == int(user_id)).first().destunc


@daosession
def get_fwd_unc(session, user_id):
    return (session.query(UserFeatures.enableunc).filter(UserFeatures.id == int(user_id)).first().enableunc == 1)


@daosession
def get_dest_busy(session, user_id):
    return session.query(UserFeatures.destbusy).filter(UserFeatures.id == int(user_id)).first().destbusy


@daosession
def get_fwd_busy(session, user_id):
    return (session.query(UserFeatures.enablebusy).filter(UserFeatures.id == int(user_id)).first().enablebusy == 1)


@daosession
def get_dest_rna(session, user_id):
    return session.query(UserFeatures.destrna).filter(UserFeatures.id == int(user_id)).first().destrna


@daosession
def get_fwd_rna(session, user_id):
    return (session.query(UserFeatures.enablerna).filter(UserFeatures.id == int(user_id)).first().enablerna == 1)


@daosession
def get_name_number(session, user_id):
    res = (session.query(UserFeatures.firstname, UserFeatures.lastname, ExtensionSchema.exten)
           .join(UserLine, and_(UserLine.user_id == int(user_id),
                                UserLine.main_line == True,
                                UserLine.main_line == True))
           .join(ExtensionSchema, UserLine.extension_id == ExtensionSchema.id)
           .filter(UserFeatures.id == user_id)
           .first())
    if not res:
        raise LookupError('Cannot find a line from this user id %s' % user_id)
    return '%s %s' % (res.firstname, res.lastname), res.exten


@daosession
def get_uuid_by_username_password(session, username, password):
    row = session.query(UserFeatures.uuid).filter(
        and_(UserFeatures.loginclient == username,
             UserFeatures.passwdclient == password)).first()

    if not row:
        raise LookupError('Invalid username or password')

    return row.uuid


@daosession
def get_device_id(session, user_id):
    row = (session.query(LineFeatures.device)
           .join(UserLine, and_(UserLine.user_id == int(user_id),
                                UserLine.main_line == True,
                                UserLine.main_line == True))
           .filter(and_(UserLine.line_id == LineFeatures.id,
                        LineFeatures.device != ''))
           .first())
    if not row:
        raise LookupError('Cannot find a device from this user id %s' % user_id)
    return row.device


@daosession
def get_context(session, user_id):
    res = (session.query(LineFeatures.context)
           .join(UserLine, and_(UserLine.line_id == LineFeatures.id,
                                UserLine.user_id == int(user_id),
                                UserLine.main_line == True,
                                UserLine.main_line == True))
           .first())

    if not res:
        return None

    return res.context


@daosession
def get_all(session):
    return session.query(UserFeatures).all()


@daosession
def delete_all(session):
    with commit_or_abort(session):
        session.query(UserFeatures).delete()


@daosession
def add_user(session, user):
    user.func_key_private_template_id = func_key_template_dao.create_private_template()

    with commit_or_abort(session):
        session.add(user)


@daosession
def delete(session, userid):
    with commit_or_abort(session):
        result = session.query(UserFeatures).filter(UserFeatures.id == userid)\
                                            .delete()
        (session.query(QueueMember).filter(QueueMember.usertype == 'user')
                                   .filter(QueueMember.userid == userid)
                                   .delete())
        (session.query(RightCallMember).filter(RightCallMember.type == 'user')
                                       .filter(RightCallMember.typeval == str(userid))
                                       .delete())
        (session.query(Callfiltermember).filter(Callfiltermember.type == 'user')
                                        .filter(Callfiltermember.typeval == str(userid))
                                        .delete())
        (session.query(Dialaction).filter(Dialaction.category == 'user')
                                  .filter(Dialaction.categoryval == str(userid))
                                  .delete())
        session.query(PhoneFunckey).filter(PhoneFunckey.iduserfeatures == userid).delete()
        (session.query(SchedulePath).filter(SchedulePath.path == 'user')
                                    .filter(SchedulePath.pathid == userid)
                                    .delete())
    return result


@daosession
def get_by_voicemailid(session, voicemailid):
    return session.query(UserFeatures).filter(UserFeatures.voicemailid == voicemailid).all()


@daosession
def get_user_config(session, user_id):
    with commit_or_abort(session):
        query = _user_config_query(session)
        user = query.filter(UserFeatures.id == user_id).first()

    if not user:
        raise LookupError('No user with ID %s' % user_id)

    return {str(user.id): _format_user(user)}


@daosession
def get_users_config(session):
    with commit_or_abort(session):
        query = _user_config_query(session)
        users = query.all()

    return dict((str(user.id), _format_user(user)) for user in users)


def _user_config_query(session):
    return (session.query(
        UserFeatures.agentid,
        UserFeatures.bsfilter,
        UserFeatures.callerid,
        UserFeatures.callrecord,
        UserFeatures.commented,
        UserFeatures.cti_profile_id,
        UserFeatures.description,
        UserFeatures.destbusy,
        UserFeatures.destrna,
        UserFeatures.destunc,
        UserFeatures.enableautomon,
        UserFeatures.enablebusy,
        UserFeatures.enableclient,
        UserFeatures.enablednd,
        UserFeatures.enablehint,
        UserFeatures.enablerna,
        UserFeatures.enableunc,
        UserFeatures.enablevoicemail,
        UserFeatures.enablexfer,
        UserFeatures.entityid,
        UserFeatures.firstname,
        UserFeatures.id,
        UserFeatures.incallfilter,
        UserFeatures.language,
        UserFeatures.lastname,
        UserFeatures.loginclient,
        UserFeatures.mobilephonenumber,
        UserFeatures.musiconhold,
        UserFeatures.outcallerid,
        UserFeatures.passwdclient,
        UserFeatures.pictureid,
        UserFeatures.preprocess_subroutine,
        UserFeatures.rightcallcode,
        UserFeatures.ringextern,
        UserFeatures.ringforward,
        UserFeatures.ringgroup,
        UserFeatures.ringintern,
        UserFeatures.ringseconds,
        UserFeatures.simultcalls,
        UserFeatures.timezone,
        UserFeatures.userfield,
        UserFeatures.voicemailid,
        UserFeatures.voicemailtype,
        LineFeatures.id.label('line_id'),
        LineFeatures.context.label('line_context'))
        .outerjoin(UserLine, and_(UserLine.main_user == True,
                                  UserLine.main_line == True,
                                  UserLine.user_id == UserFeatures.id))
        .outerjoin(LineFeatures, and_(LineFeatures.id == UserLine.line_id)))


def _format_user(user):
    fullname = '%s %s' % (user.firstname, user.lastname)
    context = user.line_context
    if user.line_id is None:
        line_list = []
    else:
        line_list = [str(user.line_id)]

    return {
        'agentid': user.agentid,
        'bsfilter': user.bsfilter,
        'callerid': user.callerid,
        'callrecord': user.callrecord,
        'commented': user.commented,
        'context': context,
        'cti_profile_id': user.cti_profile_id,
        'description': user.description,
        'destbusy': user.destbusy,
        'destrna': user.destrna,
        'destunc': user.destunc,
        'enableautomon': user.enableautomon,
        'enablebusy': user.enablebusy,
        'enableclient': user.enableclient,
        'enablednd': user.enablednd,
        'enablehint': user.enablehint,
        'enablerna': user.enablerna,
        'enableunc': user.enableunc,
        'enablevoicemail': user.enablevoicemail,
        'enablexfer': user.enablexfer,
        'entityid': user.entityid,
        'firstname': user.firstname,
        'fullname': fullname,
        'id': user.id,
        'identity': fullname,
        'incallfilter': user.incallfilter,
        'language': user.language,
        'lastname': user.lastname,
        'linelist': line_list,
        'loginclient': user.loginclient,
        'mobilephonenumber': user.mobilephonenumber,
        'musiconhold': user.musiconhold,
        'outcallerid': user.outcallerid,
        'passwdclient': user.passwdclient,
        'pictureid': user.pictureid,
        'preprocess_subroutine': user.preprocess_subroutine,
        'rightcallcode': user.rightcallcode,
        'ringextern': user.ringextern,
        'ringforward': user.ringforward,
        'ringgroup': user.ringgroup,
        'ringintern': user.ringintern,
        'ringseconds': user.ringseconds,
        'simultcalls': user.simultcalls,
        'timezone': user.timezone,
        'userfield': user.userfield,
        'voicemailid': user.voicemailid,
        'voicemailtype': user.voicemailtype,
    }


@daosession
def get_user_join_line(session, userid):
    return (session.query(UserFeatures, LineFeatures)
            .outerjoin(UserLine, and_(UserFeatures.id == UserLine.user_id,
                                      UserLine.main_user == True,
                                      UserLine.main_line == True))
            .outerjoin(LineFeatures, LineFeatures.id == UserLine.line_id)
            .filter(UserFeatures.id == userid)
            .first())


@daosession
def get_all_join_line(session):
    return (session.query(UserFeatures, LineFeatures)
            .outerjoin(UserLine, and_(UserFeatures.id == UserLine.user_id,
                                      UserLine.main_user == True,
                                      UserLine.main_line == True))
            .outerjoin(LineFeatures, LineFeatures.id == UserLine.line_id)
            .all())
