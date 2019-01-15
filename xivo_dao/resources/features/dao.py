# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.features import Features

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import daosession

from .persistor import FeaturesPersistor


@daosession
def find_all(session, section):
    return FeaturesPersistor(session).find_all(section)


@daosession
def edit_all(session, section, features):
    FeaturesPersistor(session).edit_all(section, features)


@daosession
def find_park_position_range(session):
    query = (session.query(Features.var_val)
             .filter(Features.commented == 0)
             .filter(Features.var_name == 'parkpos')
             )

    raw_range = query.scalar()
    if not raw_range:
        return None

    return tuple(int(x) for x in raw_range.split("-"))


@daosession
def get_value(session, feature_id):
    value = (session.query(Features.var_val)
             .filter(Features.id == feature_id)
             .scalar())

    if not value:
        raise errors.not_found('Features', id=feature_id)

    return value
