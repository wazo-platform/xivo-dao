# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class CallPickupPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = CallPickup

    def __init__(self, session, call_pickup_search, tenant_uuids=None):
        self.session = session
        self.search_system = call_pickup_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(CallPickup)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('CallPickup', **criteria)
        return model

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def create(self, call_pickup):
        self._fill_default_values(call_pickup)
        self.session.add(call_pickup)
        self.session.flush()
        return call_pickup

    def _fill_default_values(self, call_pickup):
        last_id = (
            self.session.query(CallPickup.id)
            .order_by(CallPickup.id.desc())
            .limit(1)
            .scalar()
        )
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
