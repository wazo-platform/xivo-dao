# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticsip import StaticSIP as RegisterSIP
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=RegisterSIP,
                      columns={'id': RegisterSIP.id},
                      default_sort='id')


class RegisterSIPSearchSystem(SearchSystem):

    def search(self, session, parameters=None):
        query = session.query(self.config.table).filter(RegisterSIP.var_name == 'register')
        return self.search_from_query(query, parameters)


register_sip_search = RegisterSIPSearchSystem(config)
