# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
