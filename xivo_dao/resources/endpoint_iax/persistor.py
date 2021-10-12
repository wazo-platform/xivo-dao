# -*- coding: utf-8 -*-
# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import partial

from xivo_dao.alchemy.useriax import UserIAX as IAX
from xivo_dao.helpers import errors, generators
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class IAXPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = IAX

    def __init__(self, session, iax_search, tenant_uuids=None):
        self.session = session
        self.search_system = iax_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(IAX)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get(self, iax_id):
        iax = self.find_by({'id': iax_id})
        if not iax:
            raise errors.not_found('IAXEndpoint', id=iax_id)
        return iax

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def create(self, iax):
        self.fill_default_values(iax)
        self.persist(iax)
        return self.get(iax.id)

    def edit(self, iax):
        self.persist(iax)
        self._fix_associated(iax)

    def delete(self, iax):
        self.session.query(IAX).filter(IAX.id == iax.id).delete()
        self._fix_associated(iax)

    def _fix_associated(self, iax):
        if iax.trunk_rel:
            TrunkFixes(self.session).fix(iax.trunk_rel.id)

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
