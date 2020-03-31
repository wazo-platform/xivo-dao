# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class TransportPersistor(CriteriaBuilderMixin):

    _search_table = PJSIPTransport

    def __init__(self, session, transport_search):
        self.session = session
        self.transport_search = transport_search

    def create(self, transport):
        self.session.add(transport)
        self.session.flush()
        return transport

    def delete(self, transport):
        self.session.delete(transport)
        self.session.flush()

    def edit(self, transport):
        self.session.add(transport)
        self.session.flush()

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def get_by(self, criteria):
        transport = self.find_by(criteria)
        if not transport:
            raise errors.not_found('Transport', **criteria)
        return transport

    def search(self, parameters):
        rows, total = self.transport_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def _find_query(self, criteria):
        query = self.session.query(PJSIPTransport)
        return self.build_criteria(query, criteria)
