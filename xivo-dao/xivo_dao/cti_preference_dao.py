# -*- coding: utf-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get(preference_id):
    return _session().query(CtiPreference).filter(CtiPreference.id == preference_id).first()


def get_name(preference_id):
    return _get(preference_id).name


def get_preferences():
    res = {}
    rows = (_session().query(CtiProfile).all())
    for row in rows:
        res[row.name] = {}

    rows = (_session().query(CtiProfile, CtiProfilePreference, CtiPreference)
            .join((CtiProfilePreference, CtiProfilePreference.profile_id == CtiProfile.id),
                  (CtiPreference, CtiProfilePreference.preference_id == CtiPreference.id))
            .all())
    for row in rows:
        cti_profile, cti_profile_preference, cti_preference = row
        profile = cti_profile.name
        option_dict = {cti_preference.option: cti_profile_preference.value}
        res[profile].update(option_dict)
    return res
