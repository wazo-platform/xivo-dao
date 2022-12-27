# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=MeetingAuthorization,
    columns={
        'guest_name': MeetingAuthorization.guest_name,
        'creation_time': MeetingAuthorization.created_at,
    },
    search=['guest_name'],
    default_sort='guest_name',
)

meeting_authorization_search = SearchSystem(config)
