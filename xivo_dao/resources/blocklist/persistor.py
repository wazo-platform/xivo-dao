# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.blocklist import Blocklist
from xivo_dao.alchemy.blocklist_number import BlocklistNumber
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, separate_criteria


class Persistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = BlocklistNumber

    def __init__(self, session, search_system, tenant_uuids=None):
        self.session = session
        self.search_system = search_system
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(BlocklistNumber).options(
            joinedload(BlocklistNumber.blocklist).joinedload(Blocklist._user_link),
        )
        if self.tenant_uuids is not None:
            query = query.filter(
                BlocklistNumber.blocklist.has(
                    Blocklist.tenant_uuid.in_(self.tenant_uuids)
                )
            )
        bulk_criteria, criteria = separate_criteria(criteria)
        query = self.build_bulk_criteria(query, bulk_criteria)
        query = self.build_criteria(query, criteria)
        return query

    def _search_query(self):
        return self.session.query(BlocklistNumber).options(
            joinedload(BlocklistNumber.blocklist).joinedload(Blocklist._user_link)
        )


class BlocklistPersistor(Persistor):
    _search_table = Blocklist

    def _find_query(self, criteria):
        query = self.session.query(Blocklist).options(
            joinedload(Blocklist._user_link),
        )
        if self.tenant_uuids is not None:
            query = query.filter(Blocklist.tenant_uuid.in_(self.tenant_uuids))

        query = self.build_criteria(query, dict(criteria))
        return query

    def _search_query(self):
        return self.session.query(Blocklist).options(joinedload(Blocklist._user_link))
