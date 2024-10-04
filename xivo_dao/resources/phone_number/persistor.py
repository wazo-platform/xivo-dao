# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.phone_number import PhoneNumber

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = PhoneNumber

    def __init__(self, session, search_system, tenant_uuids=None):
        self.session = session
        self.search_system = search_system
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(PhoneNumber)
        if self.tenant_uuids is not None:
            query = query.filter(PhoneNumber.tenant_uuid.in_(self.tenant_uuids))
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(PhoneNumber)
