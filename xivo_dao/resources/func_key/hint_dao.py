# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import (
    and_,
    bindparam,
    Integer,
    Unicode,
    literal_column,
    sql,
)
from sqlalchemy.orm import (
    aliased,
    joinedload,
)
from sqlalchemy.ext import baked
from sqlalchemy.sql.expression import true

from xivo.xivo_helpers import clean_extension

from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.func_key.model import Hint

user_extension = aliased(Extension)

agent_hints_bakery = baked.bakery()
agent_hints_query = agent_hints_bakery(
    lambda s: s.query(
        sql.cast(FuncKeyDestAgent.agent_id, Unicode).label('argument'),
        UserFeatures.id.label('user_id'),
        FeatureExtension.exten.label('feature_extension'),
    )
    .join(
        FeatureExtension,
        FeatureExtension.uuid == FuncKeyDestAgent.feature_extension_uuid,
    )
    .join(
        FuncKeyMapping,
        FuncKeyDestAgent.func_key_id == FuncKeyMapping.func_key_id,
    )
    .filter(
        FeatureExtension.enabled == true(),
    )
    .join(
        UserFeatures,
        FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
    )
    .join(
        UserLine,
        UserFeatures.id == UserLine.user_id,
    )
    .join(
        LineExtension,
        LineExtension.line_id == UserLine.line_id,
    )
    .join(
        user_extension,
        LineExtension.extension_id == user_extension.id,
    )
    .filter(
        and_(
            UserLine.main_user.is_(True),
            UserLine.main_line.is_(True),
            LineExtension.main_extension.is_(True),
            FuncKeyMapping.blf.is_(True),
        )
    )
)
agent_hints_query += lambda q: q.filter(user_extension.context == bindparam('context'))


conference_hints_bakery = baked.bakery()
conference_hints_query = conference_hints_bakery(
    lambda s: s.query(
        Conference.id.label('conference_id'), Extension.exten.label('extension')
    )
    .select_from(Conference)
    .join(FuncKeyDestConference, FuncKeyDestConference.conference_id == Conference.id)
    .join(
        Extension,
        sql.and_(
            Extension.type == 'conference',
            Extension.typeval == sql.cast(Conference.id, Unicode),
        ),
    )
)
conference_hints_query += lambda q: q.filter(Extension.context == bindparam('context'))

forwards_hints_bakery = baked.bakery()
forwards_hints_query = forwards_hints_bakery(
    lambda s: s.query(
        FeatureExtension.exten.label('feature_extension'),
        UserFeatures.id.label('user_id'),
        FuncKeyDestForward.number.label('argument'),
    )
    .join(
        FuncKeyDestForward,
        FuncKeyDestForward.feature_extension_uuid == FeatureExtension.uuid,
    )
    .join(
        FuncKeyMapping,
        FuncKeyDestForward.func_key_id == FuncKeyMapping.func_key_id,
    )
    .filter(FeatureExtension.enabled == true())
    .join(
        UserFeatures,
        FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
    )
    .join(
        UserLine,
        UserFeatures.id == UserLine.user_id,
    )
    .join(
        LineExtension,
        LineExtension.line_id == UserLine.line_id,
    )
    .join(
        user_extension,
        LineExtension.extension_id == user_extension.id,
    )
    .filter(
        and_(
            UserLine.main_user.is_(True),
            UserLine.main_line.is_(True),
            LineExtension.main_extension.is_(True),
            FuncKeyMapping.blf.is_(True),
        )
    )
)
forwards_hints_query += lambda q: q.filter(
    user_extension.context == bindparam('context')
)

user_extensions_bakery = baked.bakery()
user_extensions_query = user_extensions_bakery(
    lambda s: s.query(
        UserFeatures.id.label('user_id'),
        Extension.exten.label('extension'),
    )
    .distinct()
    .join(
        UserLine.userfeatures,
    )
    .join(
        LineExtension,
        UserLine.line_id == LineExtension.line_id,
    )
    .join(
        Extension,
        LineExtension.extension_id == Extension.id,
    )
    .filter(
        and_(
            UserLine.main_user.is_(True),
            LineExtension.main_extension.is_(True),
            UserFeatures.enablehint == 1,
        )
    )
)
user_extensions_query += lambda q: q.filter(Extension.context == bindparam('context'))

user_arguments_bakery = baked.bakery()
user_arguments_query = user_arguments_bakery(
    lambda s: s.query(
        UserFeatures.id.label('user_id'),
        sql.func.string_agg(
            sql.case(
                [
                    (
                        LineFeatures.endpoint_sip_uuid.isnot(None),
                        literal_column("'PJSIP/'") + EndpointSIP.name,
                    ),
                    (
                        LineFeatures.endpoint_sccp_id.isnot(None),
                        literal_column("'SCCP/'") + SCCPLine.name,
                    ),
                    (
                        LineFeatures.endpoint_custom_id.isnot(None),
                        UserCustom.interface,
                    ),
                ]
            ),
            literal_column("'&'"),
        ).label('argument'),
    )
    .join(
        UserLine.userfeatures,
    )
    .join(
        UserLine.linefeatures,
    )
    .outerjoin(
        EndpointSIP,
    )
    .outerjoin(
        SCCPLine,
    )
    .outerjoin(
        UserCustom,
    )
    .filter(
        and_(
            UserLine.main_user.is_(True),
            LineFeatures.commented == 0,
        )
    )
    .group_by(UserFeatures.id)
)
user_arguments_query += lambda q: q.filter(
    UserFeatures.id.in_(bindparam('user_ids', expanding=True))
)

service_hints_bakery = baked.bakery()
service_hints_query = service_hints_bakery(
    lambda s: s.query(
        FeatureExtension.exten.label('feature_extension'),
        UserFeatures.id.label('user_id'),
    )
    .join(
        FuncKeyDestService,
        FuncKeyDestService.feature_extension_uuid == FeatureExtension.uuid,
    )
    .join(
        FuncKeyMapping,
        FuncKeyDestService.func_key_id == FuncKeyMapping.func_key_id,
    )
    .filter(FeatureExtension.enabled == true())
    .join(
        UserFeatures,
        FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
    )
    .join(
        UserLine,
        UserFeatures.id == UserLine.user_id,
    )
    .join(
        LineExtension,
        LineExtension.line_id == UserLine.line_id,
    )
    .join(
        user_extension,
        LineExtension.extension_id == user_extension.id,
    )
    .filter(
        and_(
            UserLine.main_user.is_(True),
            UserLine.main_line.is_(True),
            LineExtension.main_extension.is_(True),
            FuncKeyMapping.blf.is_(True),
        )
    )
)
service_hints_query += lambda q: q.filter(
    user_extension.context == bindparam('context')
)

extenfeatures_bakery = baked.bakery()
extenfeatures_query = extenfeatures_bakery(lambda s: s.query(FeatureExtension.exten))
extenfeatures_query += lambda q: q.filter(
    FeatureExtension.feature == bindparam('feature')
)


def _find_extenfeatures(session, feature):
    return extenfeatures_query(session).params(feature=feature).scalar()


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

    user_arguments = _list_user_arguments(
        session, {item.user_id for item in user_extensions}
    )
    hints = []
    for user_id, extension in user_extensions:
        argument = user_arguments.get(user_id)
        if argument:
            hints.append(Hint(user_id=user_id, extension=extension, argument=argument))
    return tuple(hints)


@daosession
def user_shared_hints(session):
    query = session.query(UserFeatures).options(
        joinedload('user_lines').joinedload('line')
    )
    hints = []
    for user in query.all():
        ifaces = [f'Custom:{user.uuid}-mobile']
        for line in user.lines:
            if line.endpoint_custom_id:
                ifaces.append(line.name)
            elif line.endpoint_sip_uuid:
                ifaces.append(f'PJSIP/{line.name}')
            elif line.endpoint_sccp_id:
                ifaces.append(f'SCCP/{line.name}')
            else:
                ifaces.append(f'CUSTOM/{line.name}')

        if not ifaces:
            continue
        argument = '&'.join(ifaces)
        hint = Hint(user_id=user.id, extension=user.uuid, argument=argument)
        hints.append(hint)
    return hints


def _list_user_extensions(session, context):
    return user_extensions_query(session).params(context=context).all()


def _list_user_arguments(session, user_ids):
    query = user_arguments_query(session).params(user_ids=list(user_ids)).all()
    return {row.user_id: row.argument for row in query}


@daosession
def conference_hints(session, context):
    query = conference_hints_query(session).params(context=context)

    return tuple(
        Hint(conference_id=row.conference_id, extension=row.extension)
        for row in query.all()
    )


@daosession
def service_hints(session, context):
    query = service_hints_query(session).params(context=context).all()

    return tuple(
        Hint(user_id=row.user_id, extension=row.feature_extension, argument=None)
        for row in query
    )


@daosession
def forward_hints(session, context):
    query = forwards_hints_query(session).params(context=context).all()

    return tuple(
        Hint(
            user_id=row.user_id,
            extension=clean_extension(row.feature_extension),
            argument=row.argument,
        )
        for row in query
    )


@daosession
def agent_hints(session, context):
    query = agent_hints_query(session).params(context=context).all()

    return tuple(
        Hint(
            user_id=row.user_id,
            extension=clean_extension(row.feature_extension),
            argument=row.argument,
        )
        for row in query
    )


@daosession
def custom_hints(session, context):
    query = (
        session.query(
            FuncKeyDestCustom.exten.label('extension'),
        )
        .join(
            FuncKeyMapping,
            FuncKeyDestCustom.func_key_id == FuncKeyMapping.func_key_id,
        )
        .join(
            UserFeatures,
            FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
        )
        .join(
            UserLine,
            UserFeatures.id == UserLine.user_id,
        )
        .join(
            LineExtension,
            LineExtension.line_id == UserLine.line_id,
        )
        .join(
            user_extension,
            LineExtension.extension_id == user_extension.id,
        )
        .filter(
            and_(
                user_extension.context == context,
                UserLine.main_user.is_(True),
                UserLine.main_line.is_(True),
                LineExtension.main_extension.is_(True),
                FuncKeyMapping.blf.is_(True),
            )
        )
    )

    return tuple(Hint(extension=row.extension) for row in query)


@daosession
def bsfilter_hints(session, context):
    bsfilter_extension = clean_extension(_find_extenfeatures(session, 'bsfilter'))

    query = (
        session.query(
            sql.cast(FuncKeyDestBSFilter.filtermember_id, Unicode).label('argument'),
        )
        .join(
            Callfiltermember,
            Callfiltermember.id == FuncKeyDestBSFilter.filtermember_id,
        )
        .join(
            Callfilter,
            Callfilter.id == Callfiltermember.callfilterid,
        )
        .join(
            UserFeatures,
            sql.cast(Callfiltermember.typeval, Integer) == UserFeatures.id,
        )
        .join(
            UserLine,
            UserLine.user_id == UserFeatures.id,
        )
        .join(
            LineExtension,
            UserLine.line_id == LineExtension.line_id,
        )
        .join(
            Extension,
            Extension.id == LineExtension.extension_id,
        )
        .filter(
            and_(
                UserLine.main_user.is_(True),
                UserLine.main_line.is_(True),
                LineExtension.main_extension.is_(True),
                Extension.commented == 0,
                Callfilter.commented == 0,
                Extension.context == context,
            )
        )
    )

    return tuple(
        Hint(extension=bsfilter_extension, argument=row.argument) for row in query
    )


@daosession
def groupmember_hints(session, context):
    query = (
        (
            session.query(
                sql.cast(FuncKeyDestGroupMember.group_id, Unicode).label('argument'),
                UserFeatures.id.label('user_id'),
                FeatureExtension.exten.label('feature_extension'),
            )
            .join(
                FeatureExtension,
                FeatureExtension.uuid == FuncKeyDestGroupMember.feature_extension_uuid,
            )
            .join(
                FuncKeyMapping,
                FuncKeyDestGroupMember.func_key_id == FuncKeyMapping.func_key_id,
            )
            .filter(FeatureExtension.enabled == true())
        )
        .join(
            UserFeatures,
            FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
        )
        .join(
            UserLine,
            UserFeatures.id == UserLine.user_id,
        )
        .join(
            LineExtension,
            LineExtension.line_id == UserLine.line_id,
        )
        .join(
            user_extension,
            LineExtension.extension_id == user_extension.id,
        )
        .filter(
            and_(
                user_extension.context == context,
                UserLine.main_user.is_(True),
                UserLine.main_line.is_(True),
                LineExtension.main_extension.is_(True),
                FuncKeyMapping.blf.is_(True),
            )
        )
    )

    return tuple(
        Hint(
            user_id=row.user_id,
            extension=clean_extension(row.feature_extension),
            argument=row.argument,
        )
        for row in query
    )
