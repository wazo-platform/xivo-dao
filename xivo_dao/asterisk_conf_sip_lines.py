# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.asterisk_conf_sip_endpoints import SIPEndpoint, find_sip_endpoints


class SIPVoicemail(NamedTuple):
    number: str
    context: str


class SIPUser(NamedTuple):
    id: int
    uuid: str
    enableonlinerec: int
    simultcalls: int
    voicemail: SIPVoicemail | None


class SIPExtension(NamedTuple):
    exten: str
    context: str


@dataclass
class SIPLine:
    id: int
    context: str
    application_uuid: str | None
    endpoint_sip: SIPEndpoint
    users: list[SIPUser] = field(default_factory=list)
    extensions: list[SIPExtension] = field(default_factory=list)


def find_sip_lines(session):
    line_endpoint_uuids = session.query(LineFeatures.endpoint_sip_uuid).filter(
        LineFeatures.endpoint_sip_uuid.isnot(None)
    )
    endpoints = find_sip_endpoints(session, line_endpoint_uuids)
    lines = _find_lines(session, endpoints)
    _add_users(session, lines)
    _add_extensions(session, lines)
    return list(lines.values())


def _find_lines(session, endpoints):
    lines = {}
    line_rows = session.query(
        LineFeatures.id,
        LineFeatures.context,
        LineFeatures.application_uuid,
        LineFeatures.endpoint_sip_uuid,
    ).filter(LineFeatures.endpoint_sip_uuid.isnot(None))
    for row in line_rows:
        endpoint = endpoints.get(row.endpoint_sip_uuid)
        if not endpoint:
            continue
        lines[row.id] = SIPLine(
            id=row.id,
            context=row.context,
            application_uuid=row.application_uuid,
            endpoint_sip=endpoint,
        )
    return lines


def _add_users(session, lines):
    user_rows = (
        session.query(
            UserLine.line_id,
            UserFeatures.id,
            UserFeatures.uuid,
            UserFeatures.enableonlinerec,
            UserFeatures.simultcalls,
            Voicemail.mailbox.label('voicemail_number'),
            Voicemail.context.label('voicemail_context'),
        )
        .join(UserFeatures, UserFeatures.id == UserLine.user_id)
        .outerjoin(Voicemail, Voicemail.uniqueid == UserFeatures.voicemailid)
        .join(LineFeatures, LineFeatures.id == UserLine.line_id)
        .filter(LineFeatures.endpoint_sip_uuid.isnot(None))
        .order_by(UserLine.main_user.desc())
    )
    for row in user_rows:
        line = lines.get(row.line_id)
        if not line:
            continue
        voicemail = None
        if row.voicemail_number:
            voicemail = SIPVoicemail(
                number=row.voicemail_number,
                context=row.voicemail_context,
            )
        user = SIPUser(
            id=row.id,
            uuid=row.uuid,
            enableonlinerec=row.enableonlinerec,
            simultcalls=row.simultcalls,
            voicemail=voicemail,
        )
        line.users.append(user)


def _add_extensions(session, lines):
    extension_rows = (
        session.query(
            LineExtension.line_id,
            Extension.exten,
            Extension.context,
        )
        .join(Extension, Extension.id == LineExtension.extension_id)
        .join(LineFeatures, LineFeatures.id == LineExtension.line_id)
        .filter(LineFeatures.endpoint_sip_uuid.isnot(None))
        .order_by(LineExtension.main_extension.desc())
    )
    for row in extension_rows:
        line = lines.get(row.line_id)
        if not line:
            continue
        extension = SIPExtension(exten=row.exten, context=row.context)
        line.extensions.append(extension)
