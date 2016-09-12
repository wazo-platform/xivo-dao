# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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


from xivo_dao.alchemy.incall import Incall
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=Incall,
                      columns={'id': Incall.id,
                               'preprocess_subroutine': Incall.preprocess_subroutine,
                               'user_id': Incall.user_id,
                               'description': Incall.description},
                      default_sort='id')

incall_search = SearchSystem(config)
