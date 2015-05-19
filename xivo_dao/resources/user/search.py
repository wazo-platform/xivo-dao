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

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserFeatures,
                      columns={'firstname': UserFeatures.firstname,
                               'lastname': UserFeatures.lastname,
                               'fullname': (UserFeatures.firstname + " " + UserFeatures.lastname),
                               'caller_id': UserFeatures.callerid,
                               'description': UserFeatures.description,
                               'userfield': UserFeatures.userfield},
                      search=['fullname', 'caller_id', 'description', 'userfield'],
                      default_sort='lastname')

user_search = SearchSystem(config)
