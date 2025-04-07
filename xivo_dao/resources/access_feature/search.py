# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=AccessFeatures,
    columns={
        'id': AccessFeatures.id,
        'host': AccessFeatures.host,
        'feature': AccessFeatures.feature,
        'enabled': AccessFeatures.enabled,
    },
    default_sort='host',
)

access_feature_search = SearchSystem(config)
