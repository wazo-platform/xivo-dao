# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session


from .persistor import UserExternalAppPersistor
from .search import user_external_app_search


def _persistor():
    return UserExternalAppPersistor(Session, user_external_app_search)


def search(user_uuid, **parameters):
    return _persistor().search(user_uuid, parameters)


def get(user_uuid, external_app_name):
    return _persistor().get_by(user_uuid, {'name': external_app_name})


def get_by(user_uuid, **criteria):
    return _persistor().get_by(user_uuid, criteria)


def find(user_uuid, external_app_name):
    return _persistor().find_by(user_uuid, {'name': external_app_name})


def find_by(user_uuid, **criteria):
    return _persistor().find_by(user_uuid, criteria)


def find_all_by(user_uuid, **criteria):
    return _persistor().find_all_by(user_uuid, criteria)


def create(external_app):
    return _persistor().create(external_app)


def edit(external_app):
    _persistor().edit(external_app)


def delete(external_app):
    _persistor().delete(external_app)
