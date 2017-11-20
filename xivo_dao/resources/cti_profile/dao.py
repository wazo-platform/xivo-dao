# -*- coding: utf-8 -*-
# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_all(session):
    query = session.query(CtiProfile)
    return query.all()


@daosession
def get(session, profile_id):
    row = session.query(CtiProfile).filter(CtiProfile.id == profile_id).first()
    if row is None:
        raise errors.not_found('CtiProfile', id=profile_id)
    return row


@daosession
def get_id_by_name(session, cti_profile_name):
    row = session.query(CtiProfile).filter(CtiProfile.name == cti_profile_name).first()
    if row is None:
        raise errors.not_found('CtiProfile', name=cti_profile_name)
    return row.id
