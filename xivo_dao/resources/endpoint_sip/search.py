# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from sqlalchemy.sql import text

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=EndpointSIP,
    columns={
        'name': EndpointSIP.name,
        'asterisk_id': EndpointSIP.asterisk_id,
        'label': EndpointSIP.label,
        'template': EndpointSIP.template,
    },
    default_sort='label',
)


class EndpointSIPSearchSystem(SearchSystem):
    def search_from_query(self, query, parameters=None):
        if isinstance(parameters, dict):
            if uuid_param := parameters.pop('uuid', None):
                uuids = [uuid for uuid in uuid_param.split(',') if is_valid_uuid(uuid)]
                query = self._filter_exact_match_uuids(query, uuids)
            return super().search_from_query(query, parameters)

    def _filter_exact_match_uuids(self, query, uuids):
        if not uuids:
            return query.filter(text('false'))
        else:
            return query.filter(EndpointSIP.uuid.in_(uuids))


def is_valid_uuid(input):
    try:
        uuid.UUID(input)
        return True
    except ValueError:
        return False


sip_search = EndpointSIPSearchSystem(config)
