# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticiax import StaticIAX as RegisterIAX
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig

config = SearchConfig(
    table=RegisterIAX, columns={'id': RegisterIAX.id}, default_sort='id'
)


class RegisterIAXSearchSystem(SearchSystem):
    def search(self, session, parameters=None):
        query = session.query(self.config.table).filter(
            RegisterIAX.var_name == 'register'
        )
        return self.search_from_query(query, parameters)


register_iax_search = RegisterIAXSearchSystem(config)
