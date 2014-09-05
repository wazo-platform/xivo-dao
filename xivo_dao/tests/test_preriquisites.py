# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.helpers.db_utils import commit_or_abort


def recording_preriquisites(session):
    queue1 = QueueFeatures()
    queue1.id = 1
    queue1.name = 'name1'
    queue1.displayname = 'displayname'

    queue2 = QueueFeatures()
    queue2.id = 2
    queue2.name = 'name2'
    queue2.displayname = 'displayname'

    agent = AgentFeatures()
    agent.id = 1
    agent.numgroup = 1
    agent.number = '1000'
    agent.passwd = '1000'
    agent.context = 'default'
    agent.language = 'fr_FR'
    agent.description = 'my_agent'

    with commit_or_abort(session):
        session.add_all([queue1, queue2, agent])
