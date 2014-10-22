# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from sqlalchemy import sql, literal_column, Unicode, Integer
from sqlalchemy.orm import aliased

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.callfilter import Callfilter

from xivo_dao.data_handler.func_key.model import Hint


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
            .join(user_extension,
                  UserLine.extension_id == user_extension.id)
            .filter(user_extension.context == context)
            .filter(UserLine.main_user == True)
            .filter(UserLine.main_line == True)
            .filter(FuncKeyMapping.blf == True))


@daosession
def progfunckey_extension(session):
    extension = _find_extenfeatures(session, 'phoneprogfunckey')
    return extension.strip('_.')


@daosession
def calluser_extension(session):
    extension = _find_extenfeatures(session, 'calluser')
    return extension.strip('_.')


@daosession
def user_hints(session, context):
    query = (session.query(UserFeatures.id.label('user_id'),
                           Extension.exten.label('extension'),
                           sql.case([
                               (LineFeatures.protocol == 'sip', literal_column("'SIP/'") + UserSIP.name),
                               (LineFeatures.protocol == 'sccp', literal_column("'SCCP/'") + SCCPLine.name),
                               (LineFeatures.protocol == 'custom', UserCustom.interface)
                           ]).label('argument'))
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
             .join(UserLine.extensions)
             .join(FuncKeyDestUser,
                   FuncKeyDestUser.user_id == UserFeatures.id)
             .filter(UserLine.main_user == True)
             .filter(UserLine.main_line == True)
             .filter(LineFeatures.commented == 0)
             .filter(Extension.context == context)
             )

    return tuple(Hint(user_id=row.user_id,
                      extension=row.extension,
                      argument=row.argument)
                 for row in query)


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
             .filter(Extension.context == context)
             )

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
                      extension=row.extension.strip('_.'),
                      argument=row.argument)
                 for row in query)


@daosession
def agent_hints(session, context):
    agent_action = (
        sql.text("""
            SELECT
                action_tbl.agent_action AS agent_action,
                action_tbl.extension_action AS extension_action
            FROM
                (VALUES
                    ('login', 'agentstaticlogin'),
                    ('logoff', 'agentstaticlogin'),
                    ('toggle', 'agentstaticlogtoggle')
                )
                AS action_tbl(agent_action, extension_action)
                 """)
        .columns(agent_action=Unicode,
                 extension_action=Unicode)
        .alias('agent_action'))

    query = (session.query(sql.cast(FuncKeyDestAgent.agent_id, Unicode).label('argument'),
                           UserFeatures.id.label('user_id'),
                           Extension.exten.label('extension'))
             .join(agent_action,
                   FuncKeyDestAgent.action == agent_action.c.agent_action)
             .join(Extension,
                   Extension.typeval == agent_action.c.extension_action)
             .join(FuncKeyMapping,
                   FuncKeyDestAgent.func_key_id == FuncKeyMapping.func_key_id)
             .filter(Extension.commented == 0))
    query = _common_filter(query, context)

    return tuple(Hint(user_id=row.user_id,
                      extension=row.extension.strip('_.'),
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
    bsfilter_extension = _find_extenfeatures(session, 'bsfilter')
    user_extension = aliased(Extension)

    query = (session.query(Callfiltermember.id.label('argument'))
             .join(Callfilter,
                   Callfiltermember.callfilterid == Callfilter.id)
             .join(UserLine,
                   sql.and_(UserLine.user_id == sql.cast(Callfiltermember.typeval, Integer),
                            UserLine.main_user == True,
                            UserLine.main_line == True))
             .join(user_extension,
                   UserLine.extension_id == user_extension.id)
             .filter(Callfiltermember.bstype == 'secretary')
             .filter(user_extension.context == context)
             .filter(UserLine.main_user == True)
             .filter(UserLine.main_line == True)
             .filter(Callfilter.commented == 0))

    return tuple(Hint(user_id=None,
                      extension=bsfilter_extension.strip('_.'),
                      argument=str(row.argument))
                 for row in query)
