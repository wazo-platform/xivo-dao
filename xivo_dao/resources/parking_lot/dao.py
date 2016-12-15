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

from xivo_dao.helpers.db_manager import daosession

from .persistor import ParkingLotPersistor
from .search import parking_lot_search


@daosession
def search(session, **parameters):
    return ParkingLotPersistor(session, parking_lot_search).search(parameters)


@daosession
def get(session, parking_lot_id):
    return ParkingLotPersistor(session, parking_lot_search).get_by({'id': parking_lot_id})


@daosession
def get_by(session, **criteria):
    return ParkingLotPersistor(session, parking_lot_search).get_by(criteria)


@daosession
def find(session, parking_lot_id):
    return ParkingLotPersistor(session, parking_lot_search).find_by({'id': parking_lot_id})


@daosession
def find_by(session, **criteria):
    return ParkingLotPersistor(session, parking_lot_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return ParkingLotPersistor(session, parking_lot_search).find_all_by(criteria)


@daosession
def create(session, parking_lot):
    return ParkingLotPersistor(session, parking_lot_search).create(parking_lot)


@daosession
def edit(session, parking_lot):
    ParkingLotPersistor(session, parking_lot_search).edit(parking_lot)


@daosession
def delete(session, parking_lot):
    ParkingLotPersistor(session, parking_lot_search).delete(parking_lot)
