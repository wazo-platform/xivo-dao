# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=Voicemail,
    columns={
        'name': Voicemail.fullname,
        'number': Voicemail.mailbox,
        'email': Voicemail.email,
        'context': Voicemail.context,
        'language': Voicemail.language,
        'timezone': Voicemail.tz,
        'pager': Voicemail.pager,
    },
    search=['name', 'number', 'email', 'pager'],
    default_sort='number',
)

voicemail_search = SearchSystem(config)
