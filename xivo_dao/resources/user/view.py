# -*- coding: utf-8 -*-
# Copyright 2014-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func, case

from xivo_dao.resources.utils.view import ViewSelector, View
from xivo_dao.resources.user.model import UserDirectory, UserSummary

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.user_line import UserLine


class UserView(View):

    def query(self, session):
        return (session.query(User)
                .options(joinedload('agent'))
                .options(joinedload('group_members')
                         .joinedload('group'))
                .options(joinedload('incall_dialactions')
                         .joinedload('incall')
                         .joinedload('extensions'))
                .options(joinedload('user_dialactions'))
                .options(joinedload('user_lines')
                         .joinedload('line')
                         .joinedload('endpoint_sip'))
                .options(joinedload('user_lines')
                         .joinedload('line')
                         .joinedload('endpoint_sccp'))
                .options(joinedload('user_lines')
                         .joinedload('line')
                         .joinedload('endpoint_custom'))
                .options(joinedload('user_lines')
                         .joinedload('line')
                         .joinedload('line_extensions')
                         .joinedload('extension'))
                .options(joinedload('call_pickup_interceptor_pickups')
                         .joinedload('pickupmember_user_targets'))
                .options(joinedload('call_pickup_interceptor_pickups')
                         .joinedload('pickupmember_group_targets'))
                .options(joinedload('group_members'))
                .options(joinedload('queue_members'))
                .options(joinedload('switchboard_member_users'))
                .options(joinedload('schedule_paths'))
                .options(joinedload('rightcall_members'))
                .options(joinedload('voicemail')))

    def convert(self, model):
        return model


class DirectoryView(View):

    def query(self, session):
        query = (session.query(User.id.label('id'),
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
                               Extension.context.label('context')))
        return query

    def convert(self, row):
        return UserDirectory(id=row.id,
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
                             context=row.context)


class SummaryView(View):

    def query(self, session):
        query = (session.query(User.id.label('id'),
                               User.uuid.label('uuid'),
                               User.firstname.label('firstname'),
                               func.nullif(User.lastname, '').label('lastname'),
                               func.nullif(User.email, '').label('email'),
                               User.enabled.label('enabled'),
                               case([
                                   (Line.endpoint_custom_id == None, Line.provisioning_code)
                               ],
                                   else_=None).label('provisioning_code'),
                               Line.protocol.label('protocol'),
                               Extension.exten.label('extension'),
                               Extension.context.label('context')))
        return query

    def convert(self, row):
        return UserSummary(id=row.id,
                           uuid=row.uuid,
                           firstname=row.firstname,
                           lastname=row.lastname,
                           email=row.email,
                           enabled=row.enabled,
                           provisioning_code=row.provisioning_code,
                           protocol=row.protocol,
                           extension=row.extension,
                           context=row.context)


user_view = ViewSelector(default=UserView(),
                         directory=DirectoryView(),
                         summary=SummaryView())
