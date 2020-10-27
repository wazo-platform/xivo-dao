# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.user_external_app import UserExternalApp
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=UserExternalApp,
    columns={'name': UserExternalApp.name},
    default_sort='name',
)

user_external_app_search = SearchSystem(config)
