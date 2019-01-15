# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=LineFeatures,
                      columns={'context': LineFeatures.context,
                               'provisioning_code': LineFeatures.provisioningid,
                               'provisioning_extension': LineFeatures.provisioningid,
                               'position': LineFeatures.num,
                               'device_slot': LineFeatures.num,
                               'protocol': LineFeatures.protocol,
                               'device_id': LineFeatures.device,
                               'name': LineFeatures.name},
                      default_sort='name')

line_search = SearchSystem(config)
