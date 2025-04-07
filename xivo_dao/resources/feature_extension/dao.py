# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.utils.search import SearchResult

from .database import agent_action_converter, fwd_converter, service_converter
from .persistor import FeatureExtensionPersistor


def persistor():
    return FeatureExtensionPersistor(Session)


def get_by(**criteria):
    return persistor().get_by(criteria)


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def get(uuid):
    return persistor().get_by({'uuid': uuid})


def find(uuid):
    return persistor().find_by({'uuid': uuid})


def search(**parameters):
    total, items = persistor().search(parameters)
    return SearchResult(total, items)


def create(extension):
    return persistor().create(extension)


def edit(extension):
    persistor().edit(extension)


def delete(extension):
    persistor().delete(extension)


def find_all_service_extensions():
    features = service_converter.features()
    query = Session.query(
        FeatureExtension.uuid, FeatureExtension.exten, FeatureExtension.feature
    ).filter(FeatureExtension.feature.in_(features))

    return [service_converter.to_model(row) for row in query]


def find_all_forward_extensions():
    features = fwd_converter.features()
    query = Session.query(
        FeatureExtension.uuid, FeatureExtension.exten, FeatureExtension.feature
    ).filter(FeatureExtension.feature.in_(features))

    return [fwd_converter.to_model(row) for row in query]


def find_all_agent_action_extensions():
    features = agent_action_converter.features()
    query = Session.query(
        FeatureExtension.uuid, FeatureExtension.exten, FeatureExtension.feature
    ).filter(FeatureExtension.feature.in_(features))

    return [agent_action_converter.to_model(row) for row in query]
