# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class TrunkPersistor(CriteriaBuilderMixin):

    _search_table = Trunk

    def __init__(self, session, trunk_search, tenant_uuids=None):
        self.session = session
        self.trunk_search = trunk_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Trunk)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        trunk = self.find_by(criteria)
        if not trunk:
            raise errors.not_found('Trunk', **criteria)
        return trunk

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.trunk_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.trunk_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, trunk):
        self.session.add(trunk)
        self.session.flush()
        return trunk

    def edit(self, trunk):
        self.session.add(trunk)
        self.session.flush()

    def delete(self, trunk):
        if trunk.endpoint_sip_uuid:
            (self.session
             .query(EndpointSIP)
             .filter(EndpointSIP.uuid == trunk.endpoint_sip_uuid)
             .delete())
        elif trunk.endpoint_iax_id:
            (self.session
             .query(UserIAX)
             .filter(UserIAX.id == trunk.endpoint_iax_id)
             .delete())
        elif trunk.endpoint_custom_id:
            (self.session
             .query(UserCustom)
             .filter(UserCustom.id == trunk.endpoint_custom_id)
             .delete())

        if trunk.register_iax_id:
            (self.session
             .query(StaticIAX)
             .filter(StaticIAX.id == trunk.register_iax_id)
             .delete())

        self.session.delete(trunk)
        self.session.flush()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Trunk.tenant_uuid.in_(self.tenant_uuids))

    def associate_endpoint_sip(self, trunk, endpoint):
        if trunk.protocol not in ('sip', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol
            )
        trunk.endpoint_sip_uuid = endpoint.uuid
        self.session.flush()
        self.session.expire(trunk, ['endpoint_sip'])

    def dissociate_endpoint_sip(self, trunk, endpoint):
        if endpoint is trunk.endpoint_sip:
            trunk.endpoint_sip_uuid = None
            self.session.flush()
            self.session.expire(trunk, ['endpoint_sip'])

    def associate_endpoint_iax(self, trunk, endpoint):
        if trunk.protocol not in ('iax', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol
            )
        trunk.endpoint_iax_id = endpoint.id
        self.session.flush()
        self.session.expire(trunk, ['endpoint_iax'])

    def dissociate_endpoint_iax(self, trunk, endpoint):
        if endpoint is trunk.endpoint_iax:
            trunk.endpoint_iax_id = None
            self.session.flush()
            self.session.expire(trunk, ['endpoint_iax'])

    def associate_endpoint_custom(self, trunk, endpoint):
        if trunk.protocol not in ('custom', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol
            )
        trunk.endpoint_custom_id = endpoint.id
        self.session.flush()
        self.session.expire(trunk, ['endpoint_custom'])

    def dissociate_endpoint_custom(self, trunk, endpoint):
        if endpoint is trunk.endpoint_custom:
            trunk.endpoint_custom_id = None
            self.session.flush()
            self.session.expire(trunk, ['endpoint_custom'])

    def associate_register_iax(self, trunk, register):
        if trunk.protocol not in ('iax', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol
            )
        trunk.register_iax_id = register.id
        self.session.flush()
        self.session.expire(trunk, ['register_iax'])

    def dissociate_register_iax(self, trunk, register):
        if register is trunk.register_iax:
            trunk.register_iax_id = None
            self.session.flush()
            self.session.expire(trunk, ['register_iax'])
