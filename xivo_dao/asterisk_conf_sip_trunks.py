# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import NamedTuple

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.asterisk_conf_sip_endpoints import SIPEndpoint, find_sip_endpoints


class SIPTrunk(NamedTuple):
    context: str | None
    endpoint_sip: SIPEndpoint


def find_sip_trunks(session):
    trunk_endpoint_uuids = session.query(TrunkFeatures.endpoint_sip_uuid).filter(
        TrunkFeatures.endpoint_sip_uuid.isnot(None)
    )
    endpoints = find_sip_endpoints(session, trunk_endpoint_uuids)

    trunks = []
    trunk_rows = session.query(
        TrunkFeatures.context,
        TrunkFeatures.endpoint_sip_uuid,
    ).filter(TrunkFeatures.endpoint_sip_uuid.isnot(None))
    for row in trunk_rows:
        endpoint = endpoints.get(row.endpoint_sip_uuid)
        if not endpoint:
            continue
        trunks.append(SIPTrunk(context=row.context, endpoint_sip=endpoint))
    return trunks
