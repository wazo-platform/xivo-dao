# -*- coding: utf-8 -*-

# Copyright 2014-2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.context import Context
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=Extension,
                      columns={'exten': Extension.exten,
                               'context': Extension.context},
                      default_sort='exten')


class ExtensionSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters=None):
        query = self._apply_type_filter(query, parameters)
        return SearchSystem.search_from_query(self, query, parameters)

    def _apply_type_filter(self, query, parameters=None):
        if parameters and 'type' in parameters:
            return (query
                    .join(Context, Extension.context == Context.name)
                    .filter(Context.contexttype == parameters['type']))
        return query


extension_search = ExtensionSearchSystem(config)
