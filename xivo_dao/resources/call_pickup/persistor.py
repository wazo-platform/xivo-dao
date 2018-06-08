# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CallPickupPersistor(CriteriaBuilderMixin):

    _search_table = CallPickup

    def __init__(self, session, call_pickup_search):
        self.session = session
        self.call_pickup_search = call_pickup_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(CallPickup)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        call_pickup = self.find_by(criteria)
        if not call_pickup:
            raise errors.not_found('CallPickup', **criteria)
        return call_pickup

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.call_pickup_search.search(self.session, parameters)
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
        call_pickup.entity_id = Entity.query_default_id().as_scalar()

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
