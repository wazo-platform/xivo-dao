# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
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
def get_value(session, feature_id):
    value = session.query(Features.var_val).filter(Features.id == feature_id).scalar()

    if not value:
        raise errors.not_found('Features', id=feature_id)

    value = _extract_applicationmap_dtmf(value)

    return value


def _extract_applicationmap_dtmf(value):
    return value.split(',', 1)[0]
