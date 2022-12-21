# Copyright 2019-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import AccessFeaturesPersistor
from .search import access_feature_search


@daosession
def search(session, **parameters):
    return AccessFeaturesPersistor(session, access_feature_search).search(parameters)


@daosession
def get(session, access_feature_id):
    return AccessFeaturesPersistor(session, access_feature_search).get_by({'id': access_feature_id})


@daosession
def get_by(session, **criteria):
    return AccessFeaturesPersistor(session, access_feature_search).get_by(criteria)


@daosession
def find(session, access_feature_id):
    return AccessFeaturesPersistor(session, access_feature_search).find_by({'id': access_feature_id})


@daosession
def find_by(session, **criteria):
    return AccessFeaturesPersistor(session, access_feature_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return AccessFeaturesPersistor(session, access_feature_search).find_all_by(criteria)


@daosession
def create(session, access_feature):
    return AccessFeaturesPersistor(session, access_feature_search).create(access_feature)


@daosession
def edit(session, access_feature):
    AccessFeaturesPersistor(session, access_feature_search).edit(access_feature)


@daosession
def delete(session, access_feature):
    AccessFeaturesPersistor(session, access_feature_search).delete(access_feature)
