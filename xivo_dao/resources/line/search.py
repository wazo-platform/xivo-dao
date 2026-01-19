# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import sql
from sqlalchemy.sql.elements import and_

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

# NOTE(jalie): The following variables replaces hybrid_properties for
# searching by callerid's name and num because they trigger 2 full scans
# This approach queries the callerid only once and then apply transformation
# for searching
callerid_subquery = (
    EndpointSIP.build_sip_option_subquery('callerid', 'endpoint').select().cte()
)

cid_name = LineFeatures.build_caller_id_expression(
    sql.func.substring(callerid_subquery.c.value, '"([^"]+)"\\s+'), 'cid_name'
)

cid_num = LineFeatures.build_caller_id_expression(
    sql.func.substring(callerid_subquery.c.value, '<([0-9A-Z]+)?>'), 'cid_num'
)


config = SearchConfig(
    table=LineFeatures,
    columns={
        'context': LineFeatures.context,
        'provisioning_code': LineFeatures.provisioningid,
        'provisioning_extension': LineFeatures.provisioningid,
        'position': LineFeatures.num,
        'device_slot': LineFeatures.num,
        'protocol': LineFeatures.protocol,
        'device_id': LineFeatures.device,
        'name': LineFeatures.name,
        'caller_id_name': cid_name,
        'caller_id_num': cid_num,
        'exten': Extension.exten,
    },
    default_sort='name',
)


class LineSearchSystem(SearchSystem):
    def search_from_query(self, query, parameters):
        query = self._search_on_extension(query)
        query = self._search_on_endpoint_options(query, parameters)
        return super().search_from_query(query, parameters)

    def _search_on_endpoint_options(self, query, parameters):
        # NOTE (jalie): Since the callerid subquery is expensive, only join if we explicitly
        # must search on it
        search_terms = ('search', 'caller_id_name', 'caller_id_num')
        sort_terms = ('caller_id_name', 'caller_id_num')

        is_search_term = any(term in parameters for term in search_terms)
        is_sort_term = parameters.get('sort') in sort_terms

        if is_search_term or is_sort_term:
            query = query.outerjoin(
                callerid_subquery,
                callerid_subquery.c.root == LineFeatures.endpoint_sip_uuid,
            )

        return query

    def _search_on_extension(self, query):
        return query.outerjoin(
            LineExtension,
            and_(LineExtension.line_id == LineFeatures.id, LineFeatures.commented == 0),
        ).outerjoin(
            Extension,
            and_(
                LineExtension.extension_id == Extension.id,
                LineExtension.line_id == LineFeatures.id,
                Extension.commented == 0,
            ),
        )


line_search = LineSearchSystem(config)
