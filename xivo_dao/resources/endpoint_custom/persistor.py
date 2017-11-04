# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.helpers import errors
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin
from xivo_dao.resources.endpoint_custom.search import custom_search


class CustomPersistor(CriteriaBuilderMixin):

    _search_table = Custom

    def __init__(self, session):
        self.session = session

    def get(self, id):
        custom = self.session.query(Custom).filter_by(id=id).first()
        if not custom:
            raise errors.not_found('CustomEndpoint', id=id)
        return custom

    def find_query(self, criteria):
        query = self.session.query(Custom)
        return self.build_criteria(query, criteria)

    def find_by(self, criteria):
        return self.find_query(criteria).first()

    def find_all_by(self, criteria):
        return self.find_query(criteria).all()

    def search(self, params):
        rows, total = custom_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, custom):
        self.fill_default_values(custom)
        self.session.add(custom)
        self.session.flush()
        return custom

    def fill_default_values(self, custom):
        if custom.protocol is None:
            custom.protocol = 'custom'
        if custom.category is None:
            custom.category = 'user'

    def edit(self, custom):
        self.session.add(custom)
        self.session.flush()
        self._fix_associated(custom)

    def delete(self, custom):
        self.session.query(Custom).filter_by(id=custom.id).delete()
        self.session.flush()
        self._fix_associated(custom)

    def _fix_associated(self, custom):
        line_id = (self.session.query(Line.id)
                   .filter(Line.protocol == 'custom')
                   .filter(Line.protocolid == custom.id)
                   .scalar())

        if line_id:
            LineFixes(self.session).fix(line_id)

        trunk_id = (self.session.query(Trunk.id)
                    .filter(Trunk.protocol == 'custom')
                    .filter(Trunk.protocolid == custom.id)
                    .scalar())
        if trunk_id:
            TrunkFixes(self.session).fix(trunk_id)
