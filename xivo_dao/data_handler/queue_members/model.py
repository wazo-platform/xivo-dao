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
from xivo_dao.helpers.new_model import NewModel
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.queuemember import QueueMember


DB_TO_MODEL_MAPPING = {
    'penalty': 'penalty',
    'userid': 'agent_id'
}


class QueueMemberAgent(NewModel):

    def __init__(self, *args, **kwargs):
        NewModel.__init__(self, *args, **kwargs)

    FIELDS = [
        'agent_id',
        'queue_id',
        'penalty'
    ]

    MANDATORY = [
        'queue_id',
        'agent_id',
        'penalty'
    ]

    _RELATION = {}


class QueueMemberAgentDbConverter(DatabaseConverter):

    def __init__(self):
        DatabaseConverter.__init__(self, DB_TO_MODEL_MAPPING, QueueMember, QueueMemberAgent)


db_converter = QueueMemberAgentDbConverter()
