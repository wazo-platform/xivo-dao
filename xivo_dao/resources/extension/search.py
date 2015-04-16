# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
