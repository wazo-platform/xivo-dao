# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.external_app import ExternalApp
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=ExternalApp,
    columns={'name': ExternalApp.name},
    default_sort='name',
)

external_app_search = SearchSystem(config)
