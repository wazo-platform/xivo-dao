# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload, lazyload, selectinload
from sqlalchemy.sql import func, case

from xivo_dao.resources.utils.view import ViewSelector, View
from xivo_dao.resources.user.model import UserDirectory, UserSummary

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.user_line import UserLine


class PaginatedView(View):
    def query(self, session):
        return session.query(User)

    def convert(self, model):
        return model


class UserView(View):
    def query(self, session):
        return session.query(User).options(
            joinedload('agent'),
            joinedload('rightcall_members').selectinload('rightcall'),
            joinedload('group_members')
            .selectinload('group')
            .selectinload('call_pickup_interceptor_pickups')
            .options(
                selectinload('pickupmember_user_targets').selectinload('user'),
                selectinload('pickupmember_group_targets')
                .selectinload('group')
                .selectinload('user_queue_members')
                .selectinload('user'),
            ),
            joinedload('call_pickup_interceptor_pickups').options(
                selectinload('pickupmember_user_targets').selectinload('user'),
                selectinload('pickupmember_group_targets')
                .selectinload('group')
                .selectinload('user_queue_members')
                .selectinload('user'),
            ),
            joinedload('user_dialactions').selectinload('user'),
            joinedload('incall_dialactions')
            .selectinload('incall')
            .selectinload('extensions'),
            joinedload('user_lines').options(
                selectinload('line').options(
                    selectinload('application'),
                    selectinload('context_rel'),
                    selectinload('endpoint_sip').options(
                        selectinload('_endpoint_section').selectinload('_options'),
                        selectinload('_auth_section').selectinload('_options'),
                    ),
                    selectinload('endpoint_sccp'),
                    selectinload('endpoint_custom'),
                    selectinload('line_extensions').selectinload('extension'),
                    selectinload('user_lines').selectinload('user'),
                ),
            ),
            joinedload('queue_members'),
            joinedload('schedule_paths').selectinload('schedule'),
            joinedload('switchboard_member_users').selectinload('switchboard'),
            joinedload('voicemail'),
            lazyload('*'),
        )

    def convert(self, model):
        return model


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
        query = session.query(
            User.id.label('id'),
            User.uuid.label('uuid'),
            User.firstname.label('firstname'),
            func.nullif(User.lastname, '').label('lastname'),
            func.nullif(User.email, '').label('email'),
            User.enabled.label('enabled'),
            case(
                [(Line.endpoint_custom_id.is_(None), Line.provisioning_code)],
                else_=None,
            ).label('provisioning_code'),
            Line.protocol.label('protocol'),
            Extension.exten.label('extension'),
            Extension.context.label('context'),
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
        )


user_view = ViewSelector(
    default=UserView(), directory=DirectoryView(), summary=SummaryView(), paginated=PaginatedView(),
)
