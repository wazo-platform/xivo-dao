# Copyright 2014-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_, case, func

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers import errors
from xivo_dao.resources.user.model import UserDirectory, UserSummary
from xivo_dao.resources.utils.view import View, ViewSelector


class DefaultView(View):
    def __init__(self, query=None):
        self._query = query

    def query(self, session):
        if self._query:
            return self._query
        else:
            return session.query(User)

    def convert(self, row):
        return row


class DirectoryView(View):
    def query(self, session):
        query = session.query(
            User.id.label('id'),
            User.uuid.label('uuid'),
            UserLine.line_id.label('line_id'),
            User.agentid.label('agent_id'),
            User.firstname.label('firstname'),
            func.nullif(User.lastname, '').label('lastname'),
            func.nullif(User.email, '').label('email'),
            func.nullif(User.mobilephonenumber, '').label('mobile_phone_number'),
            Voicemail.mailbox.label('voicemail_number'),
            func.nullif(User.userfield, '').label('userfield'),
            func.nullif(User.description, '').label('description'),
            Extension.exten.label('exten'),
            Extension.context.label('context'),
        )
        return query

    def convert(self, row):
        return UserDirectory(
            id=row.id,
            uuid=row.uuid,
            line_id=row.line_id,
            agent_id=row.agent_id,
            firstname=row.firstname,
            lastname=row.lastname,
            email=row.email,
            mobile_phone_number=row.mobile_phone_number,
            voicemail_number=row.voicemail_number,
            exten=row.exten,
            userfield=row.userfield,
            description=row.description,
            context=row.context,
        )


class SummaryView(View):
    def query(self, session):
        webrtc_subq = EndpointSIP.build_sip_option_subquery('webrtc', 'endpoint')
        user_line = aliased(UserLine)
        line = aliased(Line)

        query = (
            session.query(
                User.id.label('id'),
                User.uuid.label('uuid'),
                User.firstname.label('firstname'),
                func.nullif(User.lastname, '').label('lastname'),
                func.nullif(User.email, '').label('email'),
                User.enabled.label('enabled'),
                case(
                    (Line.endpoint_custom_id.is_(None), Line.provisioning_code),
                    else_=None,
                ).label('provisioning_code'),
                Line.protocol.label('protocol'),
                func.coalesce(webrtc_subq.c.value == 'yes', False).label('is_webrtc'),
                Extension.exten.label('extension'),
                Extension.context.label('context'),
                User.subscription_type.label('subscription_type'),
            )
            .select_from(User)
            .outerjoin(
                user_line,
                and_(user_line.user_id == User.id, user_line.main_line.is_(True)),
            )
            .outerjoin(line, line.id == user_line.line_id)
            .outerjoin(webrtc_subq, webrtc_subq.c.root == line.endpoint_sip_uuid)
        )

        return query

    def convert(self, row):
        return UserSummary(
            id=row.id,
            uuid=row.uuid,
            firstname=row.firstname,
            lastname=row.lastname,
            email=row.email,
            enabled=row.enabled,
            provisioning_code=row.provisioning_code,
            protocol=row.protocol,
            extension=row.extension,
            context=row.context,
            subscription_type=row.subscription_type,
            is_webrtc=row.is_webrtc,
        )


class UserViewSelector(ViewSelector):
    def select(self, name=None, default_query=None):
        if not name:
            if default_query:
                return DefaultView(default_query)
            else:
                return self.default
        if name not in self.views:
            raise errors.invalid_view(name)
        return self.views[name]


user_view = UserViewSelector(
    default=DefaultView(), directory=DirectoryView(), summary=SummaryView()
)
