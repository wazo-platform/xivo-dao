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

from xivo_dao.alchemy.stat_switchboard_queue import StatSwitchboardQueue
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.switchboard.search import switchboard_search
from xivo_dao.resources.switchboard.view import switchboard_view


class SwitchboardPersistor(object):

    def __init__(self, session):
        self.session = session

    def search(self, parameters):
        query = switchboard_view.query(self.session)
        rows, total = switchboard_search.search_from_query(query, parameters)
        users = switchboard_view.convert_list(rows)
        return SearchResult(total, users)

    def stats(self, switchboard_id, start, end):
        if not self.switchboard_has_stats(switchboard_id):
            raise errors.not_found('Switchboard', id=switchboard_id)

        query = (self.session
                 .query(StatSwitchboardQueue)
                 .filter_by(queue_id=int(switchboard_id)))
        if start:
            query = query.filter(StatSwitchboardQueue.time > start)
        if end:
            query = query.filter(StatSwitchboardQueue.time < end)
        return query.all()

    def switchboard_has_stats(self, switchboard_id):
        existing = (self.session
                    .query(StatSwitchboardQueue)
                    .filter_by(queue_id=int(switchboard_id))
                    .first())
        return existing is not None
