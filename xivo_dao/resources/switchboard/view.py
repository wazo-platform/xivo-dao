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
from xivo_dao.resources.utils.view import View
from xivo_dao.resources.switchboard.model import Switchboard


class SwitchboardView(View):

    def query(self, session):
        query = session.query(StatSwitchboardQueue.queue_id.label('id')).distinct()
        return query

    def convert(self, row):
        return Switchboard(id=row.id)


switchboard_view = SwitchboardView()
