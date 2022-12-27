# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.ingress_http import IngressHTTP
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=IngressHTTP,
    columns={'uri': IngressHTTP.uri},
    default_sort='uri',
)

http_ingress_search = SearchSystem(config)
