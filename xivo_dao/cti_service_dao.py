# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.cti_service import CtiService
from xivo_dao.alchemy.cti_profile_service import CtiProfileService
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.helpers.db_manager import daosession


@daosession
def _get(session, profile_id):
    return session.query(CtiService).filter(CtiService.id == profile_id).first()


def get_name(profile_id):
    return _get(profile_id).name


@daosession
def get_services(session):
    res = {}
    rows = (session.query(CtiProfile).all())
    for row in rows:
        res[row.name] = []

    rows = (session.query(CtiProfile, CtiService)
            .join((CtiProfileService, CtiProfileService.profile_id == CtiProfile.id),
                  (CtiService, CtiProfileService.service_id == CtiService.id))
            .all())
    for row in rows:
        cti_profile, cti_service = row
        profile = cti_profile.name
        res[profile].append(cti_service.key)
    return res
