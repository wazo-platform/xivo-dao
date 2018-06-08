# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.resources.endpoint_custom.persistor import CustomPersistor


def persistor():
    return CustomPersistor(Session)


def get(id):
    return persistor().get(id)


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def search(**parameters):
    return persistor().search(parameters)


def create(custom):
    with flush_session(Session):
        return persistor().create(custom)


def edit(custom):
    with flush_session(Session):
        return persistor().edit(custom)


def delete(custom):
    with flush_session(Session):
        return persistor().delete(custom)
