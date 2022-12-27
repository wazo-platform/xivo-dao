# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=FuncKeyTemplate,
                      columns={'name': FuncKeyTemplate.name},
                      default_sort='name')


class FuncKeyTemplateSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters=None):
        query = self._apply_private_filter(query)
        return super().search_from_query(query, parameters)

    def _apply_private_filter(self, query):
        return query.filter(FuncKeyTemplate.private.is_(False))


template_search = FuncKeyTemplateSearchSystem(config)
