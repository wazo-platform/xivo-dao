# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.helpers.sequence_utils import split_by
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = PhoneNumber

    def __init__(self, session, search_system, tenant_uuids=None):
        self.session = session
        self.search_system = search_system
        self.tenant_uuids = tenant_uuids

    def build_bulk_criteria(self, query, criteria):
        for key, value in criteria.items():
            assert key.endswith('_in')
            column_name = key[:-3]
            column = self._get_column(column_name)
            query = query.filter(column.in_(value))
        return query

    def _find_query(self, criteria):
        query = self.session.query(PhoneNumber)
        if self.tenant_uuids is not None:
            query = query.filter(PhoneNumber.tenant_uuid.in_(self.tenant_uuids))
        bulk_criteria, criteria = split_by(
            criteria.items(), lambda x: x[0].endswith('_in')
        )
        query = self.build_bulk_criteria(query, dict(bulk_criteria))
        query = self.build_criteria(query, dict(criteria))
        return query

    def _search_query(self):
        return self.session.query(PhoneNumber)
