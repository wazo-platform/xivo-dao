# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from functools import partial

from xivo_dao.alchemy.useriax import UserIAX as IAX
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.helpers import errors, generators
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin

from .search import iax_search


class IAXPersistor(CriteriaBuilderMixin):

    _search_table = IAX

    def __init__(self, session):
        self.session = session

    def find_by(self, criteria):
        return self.find_query(criteria).first()

    def find_all_by(self, criteria):
        return self.find_query(criteria).all()

    def find_query(self, criteria):
        query = self.session.query(IAX)
        return self.build_criteria(query, criteria)

    def get(self, id):
        row = self.session.query(IAX).filter(IAX.id == id).first()
        if not row:
            raise errors.not_found('IAXEndpoint', id=id)
        return row

    def search(self, params):
        rows, total = iax_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, iax):
        self.fill_default_values(iax)
        self.persist(iax)
        return self.get(iax.id)

    def persist(self, iax):
        self.session.add(iax)
        self.session.flush()
        self.session.expire(iax)

    def edit(self, iax):
        self.persist(iax)
        self._fix_associated(iax)

    def delete(self, iax):
        self.session.query(IAX).filter(IAX.id == iax.id).delete()
        self._fix_associated(iax)

    def _fix_associated(self, iax):
        trunk_id = (self.session.query(Trunk.id)
                    .filter(Trunk.protocol == 'iax')
                    .filter(Trunk.protocolid == iax.id)
                    .scalar())
        if trunk_id:
            TrunkFixes(self.session).fix(trunk_id)

    def fill_default_values(self, iax):
        if iax.name is None:
            iax.name = generators.find_unused_hash(partial(self._already_exists, IAX.name))
        if iax.type is None:
            iax.type = 'friend'
        if iax.host is None:
            iax.host = 'dynamic'
        if iax.category is None:
            iax.category = 'trunk'

    def _already_exists(self, column, data):
        return self.session.query(IAX).filter(column == data).count() > 0
