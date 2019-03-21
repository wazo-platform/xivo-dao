# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import sql, literal_column, Unicode, Integer
from sqlalchemy.orm import aliased
from xivo.xivo_helpers import clean_extension

from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.func_key.model import Hint


def _find_extenfeatures(session, typeval):
    return (session.query(Extension.exten)
            .filter(Extension.context == 'xivo-features')
            .filter(Extension.type == 'extenfeatures')
            .filter(Extension.typeval == typeval)
            .scalar())


def _common_filter(query, context):
    user_extension = aliased(Extension)

    return (query.join(UserFeatures,
                       FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id)
            .join(UserLine,
                  UserFeatures.id == UserLine.user_id)
            .join(LineExtension,
                  LineExtension.line_id == UserLine.line_id)
            .join(user_extension,
                  LineExtension.extension_id == user_extension.id)
            .filter(user_extension.context == context)
            .filter(UserLine.main_user == True)
            .filter(UserLine.main_line == True)
            .filter(LineExtension.main_extension == True)
            .filter(FuncKeyMapping.blf == True))


@daosession
def progfunckey_extension(session):
    extension = _find_extenfeatures(session, 'phoneprogfunckey')
    return clean_extension(extension)


@daosession
def calluser_extension(session):
    extension = _find_extenfeatures(session, 'calluser')
    return clean_extension(extension)


@daosession
def user_hints(session, context):
    user_extensions = _list_user_extensions(session, context)
    if not user_extensions:
        return tuple()

    user_arguments = _list_user_arguments(session, set(item.user_id for item in user_extensions))
    hints = []
    for user_id, extension in user_extensions:
        argument = user_arguments.get(user_id)
        if argument:
            hints.append(Hint(user_id=user_id, extension=extension, argument=argument))
    return tuple(hints)


def _list_user_extensions(session, context):
    query = (session.query(UserFeatures.id.label('user_id'),
                           Extension.exten.label('extension'))
             .distinct()
             .join(UserLine.userfeatures)
             .join(LineExtension,
                   UserLine.line_id == LineExtension.line_id)
             .join(Extension,
                   LineExtension.extension_id == Extension.id)
             .join(FuncKeyDestUser,
                   FuncKeyDestUser.user_id == UserFeatures.id)
             .filter(UserLine.main_user == True)
             .filter(LineExtension.main_extension == True)
             .filter(Extension.context == context)
             .filter(UserFeatures.enablehint == 1))
    return query.all()


def _list_user_arguments(session, user_ids):
    query = (session.query(UserFeatures.id.label('user_id'),
                           sql.func.string_agg(sql.case([
                               (LineFeatures.protocol == 'sip', literal_column("'SIP/'") + UserSIP.name),
                               (LineFeatures.protocol == 'sccp', literal_column("'SCCP/'") + SCCPLine.name),
                               (LineFeatures.protocol == 'custom', UserCustom.interface)
                           ]), literal_column("'&'")).label('argument'))
             .join(UserLine.userfeatures)
             .join(UserLine.linefeatures)
             .outerjoin(UserSIP,
                        sql.and_(
                            LineFeatures.protocol == 'sip',
                            LineFeatures.protocolid == UserSIP.id))
             .outerjoin(SCCPLine,
                        sql.and_(
                            LineFeatures.protocol == 'sccp',
                            LineFeatures.protocolid == SCCPLine.id))
             .outerjoin(UserCustom,
                        sql.and_(
                            LineFeatures.protocol == 'custom',
                            LineFeatures.protocolid == UserCustom.id))
             .filter(UserFeatures.id.in_(user_ids))
             .filter(UserLine.main_user == True)
             .filter(LineFeatures.commented == 0)
             .group_by(UserFeatures.id))
    return {row.user_id: row.argument for row in query}


@daosession
def conference_hints(session, context):
    query = (session.query(MeetmeFeatures.confno.label('extension'))
             .join(FuncKeyDestConference,
                   FuncKeyDestConference.conference_id == MeetmeFeatures.id)
             .join(Extension,
                   sql.and_(
                       Extension.type == 'meetme',
                       Extension.typeval == sql.cast(MeetmeFeatures.id, Unicode)))
             .filter(MeetmeFeatures.commented == 0)
             .filter(Extension.context == context))

    return tuple(Hint(user_id=None,
                      extension=row.extension,
                      argument=None)
                 for row in query)


@daosession
def service_hints(session, context):
    query = (session.query(Extension.exten.label('extension'),
                           UserFeatures.id.label('user_id'))
             .join(FuncKeyDestService,
                   FuncKeyDestService.extension_id == Extension.id)
             .join(FuncKeyMapping,
                   FuncKeyDestService.func_key_id == FuncKeyMapping.func_key_id)
             .filter(Extension.commented == 0))
    query = _common_filter(query, context)

    return tuple(Hint(user_id=row.user_id,
                      extension=row.extension,
                      argument=None)
                 for row in query)


@daosession
def forward_hints(session, context):
    query = (session.query(Extension.exten.label('extension'),
                           UserFeatures.id.label('user_id'),
                           FuncKeyDestForward.number.label('argument'))
             .join(FuncKeyDestForward,
                   FuncKeyDestForward.extension_id == Extension.id)
             .join(FuncKeyMapping,
                   FuncKeyDestForward.func_key_id == FuncKeyMapping.func_key_id)
             .filter(Extension.commented == 0))
    query = _common_filter(query, context)

    return tuple(Hint(user_id=row.user_id,
                      extension=clean_extension(row.extension),
                      argument=row.argument)
                 for row in query)


@daosession
def agent_hints(session, context):
    query = (session.query(sql.cast(FuncKeyDestAgent.agent_id, Unicode).label('argument'),
                           UserFeatures.id.label('user_id'),
                           Extension.exten.label('extension'))
             .join(Extension,
                   Extension.id == FuncKeyDestAgent.extension_id)
             .join(FuncKeyMapping,
                   FuncKeyDestAgent.func_key_id == FuncKeyMapping.func_key_id)
             .filter(Extension.commented == 0))
    query = _common_filter(query, context)

    return tuple(Hint(user_id=row.user_id,
                      extension=clean_extension(row.extension),
                      argument=row.argument)
                 for row in query)


@daosession
def custom_hints(session, context):
    query = (session.query(FuncKeyDestCustom.exten.label('extension'))
             .join(FuncKeyMapping,
                   FuncKeyDestCustom.func_key_id == FuncKeyMapping.func_key_id))
    query = _common_filter(query, context)

    return tuple(Hint(user_id=None,
                      extension=row.extension,
                      argument=None)
                 for row in query)


@daosession
def bsfilter_hints(session, context):
    bsfilter_extension = clean_extension(_find_extenfeatures(session, 'bsfilter'))

    query = (session.query(sql.cast(FuncKeyDestBSFilter.filtermember_id, Unicode).label('argument'))
             .join(Callfiltermember,
                   Callfiltermember.id == FuncKeyDestBSFilter.filtermember_id)
             .join(Callfilter,
                   Callfilter.id == Callfiltermember.callfilterid)
             .join(UserFeatures,
                   sql.cast(Callfiltermember.typeval, Integer) == UserFeatures.id)
             .join(UserLine,
                   UserLine.user_id == UserFeatures.id)
             .join(LineExtension,
                   UserLine.line_id == LineExtension.line_id)
             .join(Extension,
                   Extension.id == LineExtension.extension_id)
             .filter(UserLine.main_user == True)
             .filter(UserLine.main_line == True)
             .filter(LineExtension.main_extension == True)
             .filter(Extension.commented == 0)
             .filter(Callfilter.commented == 0)
             .filter(Extension.context == context))

    return tuple(Hint(user_id=None,
                      extension=bsfilter_extension,
                      argument=row.argument)
                 for row in query)
