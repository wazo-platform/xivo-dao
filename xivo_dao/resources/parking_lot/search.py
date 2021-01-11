# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=ParkingLot,
    columns={
        'id': ParkingLot.id,
        'name': ParkingLot.name,
        'slots_start': ParkingLot.slots_start,
        'slots_end': ParkingLot.slots_end,
        'timeout': ParkingLot.timeout,
        'music_on_hold': ParkingLot.music_on_hold,
        'exten': ParkingLot.exten,
    },
    default_sort='name',
)

parking_lot_search = SearchSystem(config)
