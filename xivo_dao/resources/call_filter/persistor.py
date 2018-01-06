# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CallFilterPersistor(CriteriaBuilderMixin):

    _search_table = CallFilter

    def __init__(self, session, call_filter_search):
        self.session = session
        self.call_filter_search = call_filter_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(CallFilter)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        call_filter = self.find_by(criteria)
        if not call_filter:
            raise errors.not_found('CallFilter', **criteria)
        return call_filter

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.call_filter_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, call_filter):
        self.session.add(call_filter)
        self.session.flush()
        return call_filter

    def edit(self, call_filter):
        self.session.add(call_filter)
        self.session.flush()

    def delete(self, call_filter):
        self.session.delete(call_filter)
        self.session.flush()
