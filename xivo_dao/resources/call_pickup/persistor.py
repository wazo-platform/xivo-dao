# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CallPickupPersistor(CriteriaBuilderMixin):

    _search_table = CallPickup

    def __init__(self, session, call_pickup_search, tenant_uuids=None):
        self.session = session
        self.call_pickup_search = call_pickup_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(CallPickup)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        call_pickup = self.find_by(criteria)
        if not call_pickup:
            raise errors.not_found('CallPickup', **criteria)
        return call_pickup

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(CallPickup.tenant_uuid.in_(self.tenant_uuids))

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.call_pickup_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.call_pickup_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, call_pickup):
        self._fill_default_values(call_pickup)
        self.session.add(call_pickup)
        self.session.flush()
        return call_pickup

    def edit(self, call_pickup):
        self.session.add(call_pickup)
        self.session.flush()

    def delete(self, call_pickup):
        self.session.delete(call_pickup)
        self.session.flush()

    def _fill_default_values(self, call_pickup):
        last_id = self.session.query(CallPickup.id).order_by(CallPickup.id.desc()).limit(1).scalar()
        call_pickup.id = 1 if last_id is None else last_id + 1

    def associate_interceptor_users(self, call_pickup, users):
        call_pickup.user_interceptors = users
        self.session.flush()

    def associate_target_users(self, call_pickup, users):
        call_pickup.user_targets = users
        self.session.flush()

    def associate_interceptor_groups(self, call_pickup, groups):
        call_pickup.group_interceptors = groups
        self.session.flush()

    def associate_target_groups(self, call_pickup, groups):
        call_pickup.group_targets = groups
        self.session.flush()
