# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom

from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class TrunkPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Trunk

    def __init__(self, session, trunk_search, tenant_uuids=None):
        self.session = session
        self.search_system = trunk_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Trunk)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Trunk', **criteria)
        return model

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

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
