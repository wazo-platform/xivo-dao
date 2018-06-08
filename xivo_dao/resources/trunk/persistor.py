# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class TrunkPersistor(CriteriaBuilderMixin):

    _search_table = Trunk

    def __init__(self, session, trunk_search):
        self.session = session
        self.trunk_search = trunk_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Trunk)
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
        rows, total = self.trunk_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, trunk):
        self.session.add(trunk)
        self.session.flush()
        return trunk

    def edit(self, trunk):
        self.session.add(trunk)
        self.session.flush()

    def delete(self, trunk):
        if trunk.protocol == 'sip':
            (self.session
             .query(UserSIP)
             .filter(UserSIP.id == trunk.protocolid)
             .delete())
            if trunk.registerid:
                (self.session
                 .query(StaticSIP)
                 .filter(StaticSIP.id == trunk.registerid)
                 .delete())
        elif trunk.protocol == 'iax':
            (self.session
             .query(UserIAX)
             .filter(UserIAX.id == trunk.protocolid)
             .delete())
            if trunk.registerid:
                (self.session
                 .query(StaticIAX)
                 .filter(StaticIAX.id == trunk.registerid)
                 .delete())
        elif trunk.protocol == 'custom':
            (self.session
             .query(UserCustom)
             .filter(UserCustom.id == trunk.protocolid)
             .delete())
        self.session.delete(trunk)
        self.session.flush()

    def associate_register_iax(self, trunk, register):
        if trunk.protocol not in ('iax', None):
            raise errors.resource_associated('Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol)

        trunk.protocol = 'iax'
        trunk.registerid = register.id
        self.session.flush()
        self.session.expire(trunk, ['register_iax'])

    def dissociate_register_iax(self, trunk, register):
        if register is trunk.register_iax:
            trunk.registerid = 0
            if not trunk.protocolid:
                trunk.protocol = None
            self.session.flush()
            self.session.expire(trunk, ['register_iax'])

    def associate_register_sip(self, trunk, register):
        if trunk.protocol not in ('sip', None):
            raise errors.resource_associated('Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol)

        trunk.protocol = 'sip'
        trunk.registerid = register.id
        self.session.flush()
        self.session.expire(trunk, ['register_sip'])

    def dissociate_register_sip(self, trunk, register):
        if register is trunk.register_sip:
            trunk.registerid = 0
            if not trunk.protocolid:
                trunk.protocol = None
            self.session.flush()
            self.session.expire(trunk, ['register_sip'])
