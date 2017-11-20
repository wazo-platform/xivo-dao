# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .persistor import SwitchboardPersistor
from .search import switchboard_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return SwitchboardPersistor(session, switchboard_search).search(parameters)


@daosession
def get(session, switchboard_uuid):
    return SwitchboardPersistor(session, switchboard_search).get_by({'uuid': str(switchboard_uuid)})


@daosession
def get_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).get_by(criteria)


@daosession
def find(session, switchboard_uuid):
    return SwitchboardPersistor(session, switchboard_search).find_by({'uuid': str(switchboard_uuid)})


@daosession
def find_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).find_all_by(criteria)


@daosession
def create(session, switchboard):
    return SwitchboardPersistor(session, switchboard_search).create(switchboard)


@daosession
def edit(session, switchboard):
    return SwitchboardPersistor(session, switchboard_search).edit(switchboard)


@daosession
def delete(session, switchboard):
    SwitchboardPersistor(session, switchboard_search).delete(switchboard)
