# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference
from xivo_dao.helpers.db_manager import daosession


@daosession
def _get(session, preference_id):
    return session.query(CtiPreference).filter(CtiPreference.id == preference_id).first()


def get_name(preference_id):
    return _get(preference_id).name


@daosession
def get_preferences(session):
    res = {}
    rows = (session.query(CtiProfile).all())
    for row in rows:
        res[row.name] = {}

    rows = (session.query(CtiProfile, CtiProfilePreference, CtiPreference)
            .join((CtiProfilePreference, CtiProfilePreference.profile_id == CtiProfile.id),
                  (CtiPreference, CtiProfilePreference.preference_id == CtiPreference.id))
            .all())
    for row in rows:
        cti_profile, cti_profile_preference, cti_preference = row
        profile = cti_profile.name
        option_dict = {cti_preference.option: cti_profile_preference.value}
        res[profile].update(option_dict)
    return res
