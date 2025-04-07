# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=FeatureExtension,
    columns={'exten': FeatureExtension.exten, 'feature': FeatureExtension.feature},
    default_sort='exten',
)


feature_extension_search = SearchSystem(config)
