# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
