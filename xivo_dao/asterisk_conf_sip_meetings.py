# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import NamedTuple
from uuid import UUID

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.asterisk_conf_sip_endpoints import SIPEndpoint, find_sip_endpoints


class SIPMeeting(NamedTuple):
    uuid: UUID
    name: str | None
    guest_endpoint_sip: SIPEndpoint


def find_sip_meetings(session):
    guest_endpoint_uuids = session.query(Meeting.guest_endpoint_sip_uuid).filter(
        Meeting.guest_endpoint_sip_uuid.isnot(None)
    )
    endpoints = find_sip_endpoints(session, guest_endpoint_uuids)

    meetings = []
    meeting_rows = session.query(
        Meeting.uuid,
        Meeting.name,
        Meeting.guest_endpoint_sip_uuid,
    ).filter(Meeting.guest_endpoint_sip_uuid.isnot(None))
    for row in meeting_rows:
        endpoint = endpoints.get(row.guest_endpoint_sip_uuid)
        if not endpoint:
            continue
        meetings.append(
            SIPMeeting(uuid=row.uuid, name=row.name, guest_endpoint_sip=endpoint)
        )
    return meetings
