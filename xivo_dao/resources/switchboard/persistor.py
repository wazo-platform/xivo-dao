# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.switchboard import Switchboard

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SwitchboardPersistor(CriteriaBuilderMixin):

    _search_table = Switchboard

    def __init__(self, session, switchboard_search):
        self.session = session
        self.switchboard_search = switchboard_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Switchboard)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        switchboard = self.find_by(criteria)
        if not switchboard:
            raise errors.not_found('Switchboard', **criteria)
        return switchboard

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.switchboard_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()
        return switchboard

    def edit(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()

    def delete(self, switchboard):
        self.session.delete(switchboard)
        self.session.flush()
