# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.cti_profile.model import db_converter
from xivo_dao.data_handler.exception import ElementNotExistsError


@daosession
def find_all(session):
    rows = session.query(CtiProfile).all()
    return [db_converter.to_model(row) for row in rows]


@daosession
def get(session, profile_id):
    row = session.query(CtiProfile).filter(CtiProfile.id == profile_id).first()
    if row is None:
        raise ElementNotExistsError('cti_profile')
    return db_converter.to_model(row)
