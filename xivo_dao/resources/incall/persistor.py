# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class IncallPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Incall

    def __init__(self, session, incall_search, tenant_uuids=None):
        self.session = session
        self.search_system = incall_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Incall)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def delete(self, incall):
        self._delete_associations(incall)
        self.session.delete(incall)
        self.session.flush()

    def _delete_associations(self, incall):
        (
            self.session.query(Extension)
            .filter(Extension.type == 'incall')
            .filter(Extension.typeval == str(incall.id))
            .update({'type': 'user', 'typeval': '0'})
        )
