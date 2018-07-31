# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import flush_session

from .persistor import CustomPersistor


def persistor():
    return CustomPersistor(Session)


def get(custom_id):
    return persistor().get(custom_id)


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
