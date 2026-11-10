# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple
from uuid import UUID

from xivo_dao.alchemy.endpoint_sip import EndpointSIP, EndpointSIPTemplate
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail


class SIPTransport(NamedTuple):
    name: str | None


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
class SIPEndpoint:
    uuid: UUID
    name: str
    label: str | None
    template: bool | None
    asterisk_id: str | None
    tenant_uuid: str
    transport_uuid: UUID | None
    transport: SIPTransport
    templates: list[SIPEndpoint] = field(default_factory=list)
    aor_section_options: list = field(default_factory=list)
    auth_section_options: list = field(default_factory=list)
    endpoint_section_options: list = field(default_factory=list)
    identify_section_options: list = field(default_factory=list)
    outbound_auth_section_options: list = field(default_factory=list)
    registration_section_options: list = field(default_factory=list)
    registration_outbound_auth_section_options: list = field(default_factory=list)


@dataclass
class SIPLine:
    id: int
    context: str
    application_uuid: str | None
    endpoint_sip: SIPEndpoint
    users: list[SIPUser] = field(default_factory=list)
    extensions: list[SIPExtension] = field(default_factory=list)


def find_sip_lines(session):
    endpoints = _find_endpoints(session)
    lines = _find_lines(session, endpoints)
    _add_users(session, lines)
    _add_extensions(session, lines)
    return list(lines.values())


def _find_endpoints(session):
    endpoints = {}

    endpoint_rows = session.query(
        EndpointSIP.uuid,
        EndpointSIP.name,
        EndpointSIP.label,
        EndpointSIP.template,
        EndpointSIP.asterisk_id,
        EndpointSIP.tenant_uuid,
        EndpointSIP.transport_uuid,
        PJSIPTransport.name.label('transport_name'),
    ).outerjoin(PJSIPTransport, PJSIPTransport.uuid == EndpointSIP.transport_uuid)
    for row in endpoint_rows:
        endpoints[row.uuid] = SIPEndpoint(
            uuid=row.uuid,
            name=row.name,
            label=row.label,
            template=row.template,
            asterisk_id=row.asterisk_id,
            tenant_uuid=row.tenant_uuid,
            transport_uuid=row.transport_uuid,
            transport=SIPTransport(name=row.transport_name),
        )

    option_rows = session.query(
        EndpointSIPSection.endpoint_sip_uuid,
        EndpointSIPSection.type,
        EndpointSIPSectionOption.key,
        EndpointSIPSectionOption.value,
    ).join(
        EndpointSIPSectionOption,
        EndpointSIPSectionOption.endpoint_sip_section_uuid == EndpointSIPSection.uuid,
    )
    for row in option_rows:
        # Rows committed between queries may reference records earlier queries missed
        endpoint = endpoints.get(row.endpoint_sip_uuid)
        if not endpoint:
            continue
        section_options = getattr(endpoint, f'{row.type}_section_options')
        section_options.append((row.key, row.value))

    template_rows = session.query(
        EndpointSIPTemplate.child_uuid,
        EndpointSIPTemplate.parent_uuid,
    ).order_by(EndpointSIPTemplate.priority)
    for row in template_rows:
        child = endpoints.get(row.child_uuid)
        parent = endpoints.get(row.parent_uuid)
        if child and parent:
            child.templates.append(parent)

    return endpoints


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
        .order_by(LineExtension.main_extension.desc())
    )
    for row in extension_rows:
        line = lines.get(row.line_id)
        if not line:
            continue
        extension = SIPExtension(exten=row.exten, context=row.context)
        line.extensions.append(extension)
