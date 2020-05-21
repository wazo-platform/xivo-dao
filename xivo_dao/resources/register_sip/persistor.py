# -*- coding: utf-8 -*-
# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticsip import StaticSIP as RegisterSIP
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class RegisterSIPPersistor(CriteriaBuilderMixin):

    _search_table = RegisterSIP

    def __init__(self, session, register_sip_search):
        self.session = session
        self.register_sip_search = register_sip_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(RegisterSIP).filter(RegisterSIP.var_name == 'register')
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        register_sip = self.find_by(criteria)
        if not register_sip:
            raise errors.not_found('SIPRegister', **criteria)
        return register_sip

    def search(self, parameters):
        rows, total = self.register_sip_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, register_sip):
        self.session.add(register_sip)
        self.session.flush()
        return register_sip

    def edit(self, register_sip):
        self.session.add(register_sip)
        self.session.flush()

    def delete(self, register_sip):
        (self.session
         .query(TrunkFeatures)
         .filter(TrunkFeatures.register_sip_id == register_sip.id)
         .update({'registercommented': 0}))

        self.session.delete(register_sip)
        self.session.flush()
