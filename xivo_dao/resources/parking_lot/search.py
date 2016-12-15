# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=ParkingLot,
                      columns={'id': ParkingLot.id,
                               'name': ParkingLot.name,
                               'slots_start': ParkingLot.slots_start,
                               'slots_end': ParkingLot.slots_end,
                               'timeout': ParkingLot.timeout,
                               'music_on_hold': ParkingLot.music_on_hold},
                      default_sort='name')

parking_lot_search = SearchSystem(config)
