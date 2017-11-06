# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

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
