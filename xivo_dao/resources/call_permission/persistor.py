# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class CallPermissionPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = CallPermission

    def __init__(self, session, call_permission_search, tenant_uuids=None):
        self.session = session
        self.search_system = call_permission_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(CallPermission)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('CallPermission', **criteria)
        return model

    def _search_query(self):
        return self.session.query(self.search_system.config.table)
