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
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.cti_profile_xlet import CtiProfileXlet
from xivo_dao.alchemy.cti_xlet import CtiXlet
from xivo_dao.alchemy.cti_xlet_layout import CtiXletLayout
from sqlalchemy.sql.expression import asc

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get(profile_id):
    return _session().query(CtiProfile).filter(CtiProfile.id == profile_id).first()


def get_name(profile_id):
    return _get(profile_id).name


def get_profiles():
    rows = (_session().query(CtiProfile, CtiPresences, CtiPhoneHintsGroup, CtiProfileXlet, CtiXlet, CtiXletLayout)
            .join((CtiPresences, CtiProfile.presence_id == CtiPresences.id),
                  (CtiPhoneHintsGroup, CtiProfile.phonehints_id == CtiPhoneHintsGroup.id),
                  (CtiProfileXlet, CtiProfile.id == CtiProfileXlet.profile_id),
                  (CtiXlet, CtiProfileXlet.xlet_id == CtiXlet.id),
                  (CtiXletLayout, CtiProfileXlet.layout_id == CtiXletLayout.id))
                  .order_by(asc(CtiProfileXlet.order))
            .all())

    res = {}
    for row in rows:
        cti_profiles, cti_presences, cti_phonehints_group, cti_profile_xlet, cti_xlet, cti_xlet_layout = row
        if cti_profiles.name not in res:
            res[cti_profiles.name] = {}
            new_profile = res[cti_profiles.name]
            new_profile['name'] = cti_profiles.name
            new_profile['phonestatus'] = cti_phonehints_group.name
            new_profile['userstatus'] = cti_presences.name
            new_profile['preferences'] = 'itm_preferences_%s' % cti_profiles.name
            new_profile['services'] = 'itm_services_%s' % cti_profiles.name
            new_profile['xlets'] = []

        xlet = {}
        xlet['name'] = cti_xlet.plugin_name
        xlet['layout'] = cti_xlet_layout.name
        xlet['floating'] = cti_profile_xlet.floating
        xlet['closable'] = cti_profile_xlet.closable
        xlet['movable'] = cti_profile_xlet.movable
        xlet['scrollable'] = cti_profile_xlet.scrollable
        xlet['order'] = cti_profile_xlet.order

        res[cti_profiles.name]['xlets'].append(xlet)

    return res
