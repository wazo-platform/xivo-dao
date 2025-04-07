# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Tenant,
    columns={
        'uuid': Tenant.uuid,
    },
    default_sort='uuid',
)

tenant_search = SearchSystem(config)
