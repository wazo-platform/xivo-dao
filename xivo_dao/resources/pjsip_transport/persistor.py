# -*- coding: utf-8 -*-
# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class TransportPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = PJSIPTransport

    def __init__(self, session, transport_search):
        self.session = session
        self.transport_search = transport_search

    def delete(self, transport, fallback=None):
        if fallback:
            self._update_transport(transport, fallback)
        self.session.delete(transport)
        self.session.flush()

    def _update_transport(self, current, new):
        (
            self.session.query(EndpointSIP)
            .filter(EndpointSIP.transport_uuid == current.uuid)
            .update({'transport_uuid': new.uuid})
        )

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Transport', **criteria)
        return model

    def search(self, parameters):
        rows, total = self.transport_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def _find_query(self, criteria):
        query = self.session.query(PJSIPTransport)
        return self.build_criteria(query, criteria)
