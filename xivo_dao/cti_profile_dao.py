# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.cti_profile_xlet import CtiProfileXlet
from xivo_dao.alchemy.cti_xlet import CtiXlet
from xivo_dao.alchemy.cti_xlet_layout import CtiXletLayout
from sqlalchemy.sql.expression import asc
from xivo_dao.helpers.db_manager import daosession


@daosession
def _get(session, profile_id):
    return session.query(CtiProfile).filter(CtiProfile.id == profile_id).first()


def get_name(profile_id):
    return _get(profile_id).name


@daosession
def get_profiles(session):
    rows = (session.query(CtiProfile, CtiPresences, CtiPhoneHintsGroup, CtiProfileXlet, CtiXlet, CtiXletLayout)
            .join((CtiPresences, CtiProfile.presence_id == CtiPresences.id),
                  (CtiPhoneHintsGroup, CtiProfile.phonehints_id == CtiPhoneHintsGroup.id),
                  (CtiProfileXlet, CtiProfile.id == CtiProfileXlet.profile_id),
                  (CtiXlet, CtiProfileXlet.xlet_id == CtiXlet.id),
                  (CtiXletLayout, CtiProfileXlet.layout_id == CtiXletLayout.id))
            .order_by(asc(CtiProfileXlet.order))
            .all())

    res = {}
    for row in rows:
        cti_profile, cti_presences, cti_phonehints_group, cti_profile_xlet, cti_xlet, cti_xlet_layout = row
        cti_profile_id = cti_profile.id
        if cti_profile_id not in res:
            res[cti_profile_id] = {}
            new_profile = res[cti_profile_id]
            new_profile['id'] = cti_profile.id
            new_profile['name'] = cti_profile.name
            new_profile['phonestatus'] = cti_phonehints_group.name
            new_profile['userstatus'] = cti_presences.name
            new_profile['preferences'] = 'itm_preferences_%s' % cti_profile.name
            new_profile['services'] = 'itm_services_%s' % cti_profile.name
            new_profile['xlets'] = []

        xlet = {}
        xlet['name'] = cti_xlet.plugin_name
        xlet['layout'] = cti_xlet_layout.name
        xlet['floating'] = cti_profile_xlet.floating
        xlet['closable'] = cti_profile_xlet.closable
        xlet['movable'] = cti_profile_xlet.movable
        xlet['scrollable'] = cti_profile_xlet.scrollable
        xlet['order'] = cti_profile_xlet.order

        res[cti_profile_id]['xlets'].append(xlet)

    return res
