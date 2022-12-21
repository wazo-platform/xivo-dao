# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class ParkingLotPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = ParkingLot

    def __init__(self, session, parking_lot_search, tenant_uuids=None):
        self.session = session
        self.search_system = parking_lot_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(ParkingLot)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def delete(self, parking_lot):
        self._delete_associations(parking_lot)
        self.session.delete(parking_lot)
        self.session.flush()

    def _delete_associations(self, parking_lot):
        for extension in parking_lot.extensions:
            extension.type = 'user'
            extension.typeval = '0'
