# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple
from uuid import UUID

from xivo_dao.alchemy.endpoint_sip import EndpointSIP, EndpointSIPTemplate
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport


class SIPTransport(NamedTuple):
    name: str | None


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


def find_sip_endpoints(session, endpoint_uuids):
    reachable_uuids = _with_inherited_templates(session, endpoint_uuids)
    endpoints = _find_endpoints(session, reachable_uuids)
    _add_options(session, endpoints, reachable_uuids)
    _add_templates(session, endpoints, reachable_uuids)
    return endpoints


def _with_inherited_templates(session, endpoint_uuids):
    reachable = (
        session.query(EndpointSIP.uuid.label('uuid'))
        .filter(EndpointSIP.uuid.in_(endpoint_uuids))
        .cte('reachable_endpoint_sip', recursive=True)
    )
    # UNION, not UNION ALL: shared templates are listed once and a cycle ends
    reachable = reachable.union(
        session.query(EndpointSIPTemplate.parent_uuid).join(
            reachable, EndpointSIPTemplate.child_uuid == reachable.c.uuid
        )
    )
    return session.query(reachable.c.uuid)


def _find_endpoints(session, reachable_uuids):
    endpoint_rows = (
        session.query(
            EndpointSIP.uuid,
            EndpointSIP.name,
            EndpointSIP.label,
            EndpointSIP.template,
            EndpointSIP.asterisk_id,
            EndpointSIP.tenant_uuid,
            EndpointSIP.transport_uuid,
            PJSIPTransport.name.label('transport_name'),
        )
        .outerjoin(PJSIPTransport, PJSIPTransport.uuid == EndpointSIP.transport_uuid)
        .filter(EndpointSIP.uuid.in_(reachable_uuids))
    )
    return {
        row.uuid: SIPEndpoint(
            uuid=row.uuid,
            name=row.name,
            label=row.label,
            template=row.template,
            asterisk_id=row.asterisk_id,
            tenant_uuid=row.tenant_uuid,
            transport_uuid=row.transport_uuid,
            transport=SIPTransport(name=row.transport_name),
        )
        for row in endpoint_rows
    }


def _add_options(session, endpoints, reachable_uuids):
    option_rows = (
        session.query(
            EndpointSIPSection.endpoint_sip_uuid,
            EndpointSIPSection.type,
            EndpointSIPSectionOption.key,
            EndpointSIPSectionOption.value,
        )
        .join(
            EndpointSIPSectionOption,
            EndpointSIPSectionOption.endpoint_sip_section_uuid
            == EndpointSIPSection.uuid,
        )
        .filter(EndpointSIPSection.endpoint_sip_uuid.in_(reachable_uuids))
    )
    for row in option_rows:
        # Rows committed between queries may reference records earlier queries missed
        endpoint = endpoints.get(row.endpoint_sip_uuid)
        if not endpoint:
            continue
        section_options = getattr(endpoint, f'{row.type}_section_options')
        section_options.append((row.key, row.value))


def _add_templates(session, endpoints, reachable_uuids):
    template_rows = (
        session.query(
            EndpointSIPTemplate.child_uuid,
            EndpointSIPTemplate.parent_uuid,
        )
        .filter(EndpointSIPTemplate.child_uuid.in_(reachable_uuids))
        .order_by(EndpointSIPTemplate.priority)
    )
    for row in template_rows:
        child = endpoints.get(row.child_uuid)
        parent = endpoints.get(row.parent_uuid)
        if child and parent:
            child.templates.append(parent)
