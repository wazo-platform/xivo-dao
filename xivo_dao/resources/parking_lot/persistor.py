# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text

from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class ParkingLotPersistor(CriteriaBuilderMixin):

    _search_table = ParkingLot

    def __init__(self, session, parking_lot_search, tenant_uuids=None):
        self.session = session
        self.parking_lot_search = parking_lot_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(ParkingLot)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        parking_lot = self.find_by(criteria)
        if not parking_lot:
            raise errors.not_found('ParkingLot', **criteria)
        return parking_lot

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.parking_lot_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.parking_lot_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(ParkingLot.tenant_uuid.in_(self.tenant_uuids))

    def create(self, parking_lot):
        self.session.add(parking_lot)
        self.session.flush()
        return parking_lot

    def edit(self, parking_lot):
        self.session.add(parking_lot)
        self.session.flush()

    def delete(self, parking_lot):
        self.session.delete(parking_lot)
        self.session.flush()
