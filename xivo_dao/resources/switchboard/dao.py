# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .persistor import SwitchboardPersistor
from .search import switchboard_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def _persistor(session):
    return SwitchboardPersistor(session, switchboard_search)


@daosession
def search(session, **parameters):
    return _persistor().search(parameters)


@daosession
def get(session, switchboard_uuid):
    return _persistor().get_by({'uuid': str(switchboard_uuid)})


@daosession
def get_by(session, **criteria):
    return _persistor().get_by(criteria)


@daosession
def find(session, switchboard_uuid):
    return _persistor().find_by({'uuid': str(switchboard_uuid)})


@daosession
def find_by(session, **criteria):
    return _persistor().find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return _persistor().find_all_by(criteria)


@daosession
def create(session, switchboard):
    return _persistor().create(switchboard)


@daosession
def edit(session, switchboard):
    return _persistor().edit(switchboard)


@daosession
def delete(session, switchboard):
    _persistor().delete(switchboard)
