# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticiax import StaticIAX as RegisterIAX
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class RegisterIAXPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = RegisterIAX

    def __init__(self, session, register_iax_search):
        self.session = session
        self.register_iax_search = register_iax_search

    def _find_query(self, criteria):
        query = self.session.query(RegisterIAX).filter(
            RegisterIAX.var_name == 'register'
        )
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('IAXRegister', **criteria)
        return model

    def search(self, parameters):
        rows, total = self.register_iax_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def delete(self, register_iax):
        (
            self.session.query(TrunkFeatures)
            .filter(TrunkFeatures.register_iax_id == register_iax.id)
            .update({'registercommented': 0})
        )

        self.session.delete(register_iax)
        self.session.flush()
