# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.cti_service import CtiService
from xivo_dao.alchemy.cti_profile_service import CtiProfileService
from xivo_dao.alchemy.cti_profile import CtiProfile

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get(profile_id):
    return _session().query(CtiService).filter(CtiService.id == profile_id).first()


def get_name(profile_id):
    return _get(profile_id).name


def get_services():
    res = {}
    rows = (_session().query(CtiProfile).all())
    for row in rows:
        res[row.name] = []

    rows = (_session().query(CtiProfile, CtiService)
            .join((CtiProfileService, CtiProfileService.profile_id == CtiProfile.id),
                  (CtiService, CtiProfileService.service_id == CtiService.id))
            .all())
    for row in rows:
        cti_profile, cti_service = row
        profile = cti_profile.name
        res[profile].append(cti_service.key)
    return res
