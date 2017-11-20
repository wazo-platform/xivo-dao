# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=FuncKeyTemplate,
                      columns={'name': FuncKeyTemplate.name},
                      default_sort='name')


class FuncKeyTemplateSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters=None):
        query = self._apply_private_filter(query)
        return super(FuncKeyTemplateSearchSystem, self).search_from_query(query, parameters)

    def _apply_private_filter(self, query):
        return (query
                .filter(FuncKeyTemplate.private == False)
                )


template_search = FuncKeyTemplateSearchSystem(config)
