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

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.data_handler.utils.search import SearchSystem
from xivo_dao.data_handler.utils.search import SearchConfig


config = SearchConfig(table=Voicemail,
                      columns={'name': Voicemail.fullname,
                               'number': Voicemail.mailbox,
                               'email': Voicemail.email,
                               'context': Voicemail.context,
                               'language': Voicemail.language,
                               'timezone': Voicemail.tz},
                      search=['name', 'number', 'email'],
                      default_sort='number')

voicemail_search = SearchSystem(config)
